# epd-writer
Typewriter using e-ink technology. A low-tech, high latency typewriter.


# key binding
Source : https://askubuntu.com/questions/147128/change-default-tty-shortcut
and https://www.techrepublic.com/article/find-and-bind-key-sequences-in-bash/

1. Find keybinding associated with F1 key using *read* command and pressing F1
$ read
^[[[A
Make sure you write the key sequence as \e[[A rather than ^[[[A.
This is because the ^[ sequence is
equivalent to the [Esc] key, which is represented by \e in the shell. So, for instance, if the key sequence was ^[[OP the resulting bind code to use would be \e[OP.

2. Add the following line to you .bashrc
For F1 key
bind '"\e[[A": ". ~/launcher.sh\n" '
Or for F9 key
bind '"\e[20~": ". ~/launcher.sh\n" '
3. create a launcher file in your home directory

# READ stdin
https://stackoverflow.com/questions/7741930/getchar-and-stdin
gcc inread.c -o inread

# Functions keys
```
F1 : 27 91 91 65
F2 : 27 91 91 66
F3 : 
F6 : 27 91 49 55 126
à : 195 160
ù : 195 185
À : 195 128
ï : 195 175
— : 226 128 148
« . 194 171
» : 194 187
  : 194 160 (espace insécable)
```

# Backup
To enable backup to a remote ssh server, make sure to enable scp using key
cd .ssh
ssh-copy-id -i id_rsa user@BACKUP_IP

# start program 
see .bashrc file

# Splash
splash images on startup and shutdown are located in pic directory
mountain.bmp : startup image
beach.bmp : shutdown image
Need a 800x480 grayscale BMP image

# Reading keyboard input
When writing text, keyboard strokes are captured through C programs
```bash 
gcc -o inkey inkey.c
gcc -o arrowkeys arrowkeys.c
gcc -o readname readname.c
```

- INKEY : Used to capture text when writing a new file.
- READNAME : Used to capture filename, when creating a new file (F1)
- ARROWKEYS : Used to navigate when reading a file (F2)
  
