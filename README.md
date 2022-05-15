# epd-writer
Typewriter using e-ink technology

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
bind '"\e[[A": ". ~/launcher.sh\n" '

3. create a launcher file in your home directory

# READ stdin
https://stackoverflow.com/questions/7741930/getchar-and-stdin
gcc inread.c -o inread

# Functions keys
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

  # TODO
  Catch errors
  check if subprocess.popen is independant from python process
  