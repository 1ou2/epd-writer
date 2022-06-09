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


int exiterror(int fp, struct termios *tty_opts_backup){
    fprintf( stderr, "Error is %s (errno=%d)\n", strerror( errno ), errno );
    close(fp);

    // Restore previous TTY settings
    tcsetattr(STDIN_FILENO, TCSANOW, tty_opts_backup);
    exit(EX_IOERR);
}

/*
* read key strokes, and write selected actions to a file
* 
* if right arrow or up arrow pressed : add a "+"
* if down or left arrow : add a "-"
*
* program exits with CTRL-C or ESC ESC or ESC RETURN
*/
int main(int argc, char *argv[]) {
    
    int result = remove("input.arrow");

    if (result == 0)
        printf("input.arrow file deleted successfully. \n");
    else
    {
        printf("Unable to delete the file. \n");
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
    int fp = open("input.arrow", O_WRONLY | O_CREAT | O_TRUNC,S_IRWXU |S_IRWXG|S_IRWXO );
    if (fp == -1) {
        //fprintf( stderr, "Error is %s (errno=%d)\n", strerror( errno ), errno );
        //exit(EX_IOERR);
        //printf("1 - Error is %s (errno=%d)\n", strerror( errno ), errno );
        exiterror(fp,&tty_opts_backup);
    }
    printf("Opening file input.arrow\n");
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
    for (c = getchar(); c != 3; c = getchar()) {
        if (c == EOF) {
            perror("getchar error");
            exiterror(fp,&tty_opts_backup);
        }
        
        

        if (c == 27) {
            c0 = c;
            c1 = getchar();
            // exit program if ESC is pressed twice
            // or ESC + ENTER
            if (c1 == 27 || c1 == 13) {
                break;
            }
            // second key code is 91, could be F1, F2, arrow etc...
            if (c1 == 91) {
                c2 = getchar();
                // 27 91 67 is right arrow
                // 27 91 65 up
                if (c2 ==67 || c2 == 65) {
                    // write + in file : keycode 43
                    if (keypressed(43,fp) == -1){
                        perror("keypressed - char - error");
                        exiterror(fp,&tty_opts_backup);
                    }
                    c0=0;c1=0;c2=0;
                }
                // 27 91 66 down
                // 27 91 68 left
                else if (c2 == 68 || c2 == 66) {
                    if (keypressed(45,fp) == -1){
                        perror("keypressed - char - error");
                        exiterror(fp,&tty_opts_backup);
                    }
                    c0=0;c1=0;c2=0;
                }
                else {
                    c0=0;c1=0;c2=0;
                }

            }
            // non arrow escape sequence
            else {
                c0=0;c1=0;c2=0;
            }
        }
        else {
            printf("%d. 0x%02x (0%02o) %d\r\n", i++, c, c,c);
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