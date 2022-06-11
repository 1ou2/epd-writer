#include <stdio.h>
#include <string.h>
#include <unistd.h>   // STDIN_FILENO, isatty(), ttyname()
#include <stdlib.h>   // exit()
#include <termios.h>
#include <fcntl.h> 
#include <sysexits.h> // for exit status code 
#include <sys/types.h> // for umask
#include <sys/stat.h>  // for umask
#include <errno.h>

// history of character sizes
// used to handle backspace
int hindex = 0;
int history[100];

// one key was pressed 
// k : the value of the key
// fp : file handle where character will be saved
int keypressed(int k,int fp) {
    char data[10];
    data[0]=k;
    ssize_t count;
    count = write(fp,data,1);
    if (count == -1) {
        fprintf( stderr, "Error is %s (errno=%d)\n", strerror( errno ), errno );
        return -1;
    }
    history[hindex] = 1;
    hindex++;
    return 0;
}

// one key was pressed 
// c0, c1 : some characters like é are encoded by two bytes
// fp : file handle where character will be saved
int keypressed2(int c0, int c1, int fp) {
    ssize_t count;
    char data[10];
    data[0]=c0;
    count = write(fp,data,1);
    if (count == -1) {
        fprintf( stderr, "Error is %s (errno=%d)\n", strerror( errno ), errno );
        return -1;
    }
    data[0]=c1;
    count = write(fp,data,1);
    if (count == -1) {
        fprintf( stderr, "Error is %s (errno=%d)\n", strerror( errno ), errno );
        return -1;
    }
    history[hindex] = 2;
    hindex++;
    return 0;
}

// one key was pressed 
// c0, c1,c3 : some characters like — (tiret cadratin) are encoded by three bytes
// fp : file handle where character will be saved
int keypressed3(int c0, int c1, int c2, int fp) {
    char data[10];
    ssize_t count;
    data[0]=c0;
    count = write(fp,data,1);
    if (count == -1) {
        fprintf( stderr, "Error is %s (errno=%d)\n", strerror( errno ), errno );
        return -1;
    }
    data[0]=c1;
    count = write(fp,data,1);
    if (count == -1) {
        fprintf( stderr, "Error is %s (errno=%d)\n", strerror( errno ), errno );
        return -1;
    }
    data[0]=c2;
    count = write(fp,data,1);
    if (count == -1) {
        fprintf( stderr, "Error is %s (errno=%d)\n", strerror( errno ), errno );
        return -1;
    }
    history[hindex] = 3;
    hindex++;
    return 0;
}
int exiterror(int fp, struct termios *tty_opts_backup){
    fprintf( stderr, "Error is %s (errno=%d)\n", strerror( errno ), errno );
    close(fp);

    // Restore previous TTY settings
    tcsetattr(STDIN_FILENO, TCSANOW, tty_opts_backup);
    exit(EX_IOERR);
}
int main(int argc, char *argv[]) {
    if (argc != 2){
        printf("Usage : inkey filename\r\n");
        exit(EX_USAGE);
    }

    struct termios tty_opts_backup, tty_opts_raw;
    char data[10];
    
    
    if (!isatty(STDIN_FILENO)) {
      printf("Error: stdin is not a TTY\n");
      exit(EX_IOERR);
    }
    printf("stdin is %s\n", ttyname(STDIN_FILENO));

    // Back up current TTY settings
    tcgetattr(STDIN_FILENO, &tty_opts_backup);

    // Change TTY settings to raw mode
    cfmakeraw(&tty_opts_raw);
    tcsetattr(STDIN_FILENO, TCSANOW, &tty_opts_raw);


    // open file from arguments
    // FIXME : need to give right access to everyone as the waveshare module writes file as root
    // unset default umask
    umask(0);
    // open file with write permission for all
    int fp = open(argv[1], O_RDWR | O_CREAT,S_IRWXU |S_IRWXG|S_IRWXO );
    if (fp == -1) {
        //fprintf( stderr, "Error is %s (errno=%d)\n", strerror( errno ), errno );
        //exit(EX_IOERR);
        //printf("1 - Error is %s (errno=%d)\n", strerror( errno ), errno );
        exiterror(fp,&tty_opts_backup);
    }
    printf("Opening file %s",argv[1]);
    // go to end of file
    off_t offset;
    offset = lseek(fp, 0, SEEK_END);
    if (offset == -1) {
        exiterror(fp,&tty_opts_backup);
    }

    // some keys output several characters
    // e.g. : F1 is 4 chars -> 27 91 91 65
    int func=0,charsize=1,c0=0,c1=0,c2=0,c3=0,c4=0;
    // store for backspace
    int lastsize=1;
    
    
    // Read and print characters from stdin
    int c, i = 1;
    for (c = getchar(); c != 3 && c != 27; c = getchar()) {
        if (c == EOF) {
            perror("getchar error");
            exiterror(fp,&tty_opts_backup);
        }
        printf("%d. 0x%02x (0%02o) %d\r\n", i++, c, c,c);
        if (c==127 && hindex > 0) {
            hindex--;
            printf("Backspace %d\r\n",history[hindex]);
            // go back with lseek
            // but depending on character number of bytes varies
            // e.g : a -> one byte
            // é -> two bytes
            int ksize = history[hindex];
            offset = lseek(fp,0-ksize,SEEK_CUR);
            if (offset == -1) {
                perror("lseek 1 error");
                exiterror(fp,&tty_opts_backup);
            }
            // SPACE
            data[0] = 32;
            // replace with a space in the file
            for(i=0;i<ksize;i++){
                count = write(fp,data,1);
                if (count == -1) {
                    fprintf( stderr, "Error is %s (errno=%d)\n", strerror( errno ), errno );
                    return -1;
                }
            }
            // go back again
            offset = lseek(fp,0-ksize,SEEK_CUR);
            if (offset == -1) {
                perror("lseek 2 error");
                exiterror(fp,&tty_opts_backup);
            }
        }
        else if (c==13) {
            printf("ENTER\r\n");
            // use line feed in unix system : ASCII CODE = 10
            if (keypressed(10,fp) == -1) {
                perror("keypressed error");
                exiterror(fp,&tty_opts_backup);
            }
        }
        // F1 : 27 91 91 65
        // F2 : 27 91 91 66
        // ESCAPE character found
        // multi character sequence
        else if (c==27) {
            printf("ESC\r\n");
            func = 1;
            c0 = c;c1=0,c2=0,c3=0,c4=0;
        }
        // multichar character starts with 194 or 195
        // ï : 195 175
        // « : 194 171
        else if ((charsize == 1) && (c==194 || c==195)) {
            charsize = 2;
            c0 = c;
        }
        // — : 226 128 148
        else if (charsize == 1 && c==226 ) {
            charsize = 3;
            c0 = c;
        }
        else {

            if (charsize == 1 ) { 
                data[0] = c;
                if (keypressed(c,fp) == -1){
                    perror("keypressed - char - error");
                    exiterror(fp,&tty_opts_backup);
                }
            }
            else if (charsize == 2 ) { 
                if (keypressed2(c0,c,fp)==-1) {
                    perror("keypressed 2 error");
                    exiterror(fp,&tty_opts_backup);
                }

                c0 = 0;
                charsize = 1;
                lastsize = 2;
                
            }
            else if (charsize == 3) {
                if (c == 128 ) { 
                    c1 = c;
                }
                else {
                    if (keypressed3(c0,c1,c,fp) == -1) {
                        perror("keypressed 3 error");
                        exiterror(fp,&tty_opts_backup);
                    }
                    c0 = 0;c1=0;
                    charsize = 1;
                    lastsize = 3;
                }
            }

        }
        
    }
    if (c==3){
        printf("You typed 0x03 (003). Exiting.\r\n");
    }
    else if (c== 27) {
        printf("You typed ECHAP. Exiting.\r\n");
    }
    
    close(fp);
    // Restore previous TTY settings
    tcsetattr(STDIN_FILENO, TCSANOW, &tty_opts_backup);

}