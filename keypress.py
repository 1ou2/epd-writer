import fcntl
import sys,select
import os
import time
import tty
import termios
from keysconfig import *
from threading import Thread


class KeyController:
    def __init__(self,timeout=5) -> None:
        self.timeout = timeout
        pass

    def keyfunc(self):

        while True:
            k = self.keypress()
            print(k)
            # control-C
            if k[0] == '\x03':
                break
            # function key
            if k[0] == '\x1b':
                fnum = 0
                for i,fkey in enumerate(FUNC_KEYS):
                    if k == fkey:
                        fnum = i + 1
                if fnum:
                    print("function key pressed F"+str(fnum))
        
            time.sleep(.1)

    def getKey(self):
        keythread = Thread(target=self.keypress)
        keythread.start()
        

    def keypress(self):
        """Waits for a single keypress on stdin.

        This is a silly function to call if you need to do it a lot because it has
        to store stdin's current setup, setup stdin for reading single keystrokes
        then read the single keystroke then revert stdin back after reading the
        keystroke.

        Returns a tuple of characters of the key that was pressed - on Linux, 
        pressing keys like up arrow results in a sequence of characters. Returns 
        ('\x03',) on KeyboardInterrupt which can happen when a signal gets
        handled.

        """
        import termios, fcntl, sys, os
        fd = sys.stdin.fileno()
        # save old state
        flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
        attrs_save = termios.tcgetattr(fd)
        # make raw - the way to do this comes from the termios(3) man page.
        attrs = list(attrs_save) # copy the stored version to update
        # iflag
        attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK
                    | termios.ISTRIP | termios.INLCR | termios. IGNCR
                    | termios.ICRNL | termios.IXON )
        # oflag
        attrs[1] &= ~termios.OPOST
        # cflag
        attrs[2] &= ~(termios.CSIZE | termios. PARENB)
        attrs[2] |= termios.CS8
        # lflag
        attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON
                    | termios.ISIG | termios.IEXTEN)
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        # turn off non-blocking
        fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
        # read a single keystroke
        ret = []
        try:
            # wait for timeout second or a key pressed in stdin
            
            i, o, e = select.select( [sys.stdin], [], [], self.timeout )
            if i:
                ret.append(sys.stdin.read(1)) # returns a single character
                fcntl.fcntl(fd, fcntl.F_SETFL, flags_save | os.O_NONBLOCK)
                c = sys.stdin.read(1) # returns a single character
                while len(c) > 0:
                    ret.append(c)
                    c = sys.stdin.read(1)
            else:
                print("TIMEOUT on keypressed")
                ret.append(KEYTIMEOUT[0])
        #except KeyboardInterrupt:
        #    ret.append('\x03')
        finally:
            # restore old state
            termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
        return tuple(ret)

    def waitKey(self,keylist):
        while True:
            k = self.keypress()
            if k in keylist:
                return k

    def getText(self):
        text = ""
        while True:
            k = self.keypress()
            if k == ENTER:
                return text
            elif k == BACKSPACE:
                if len(text) > 0:
                    text = text[:-1]
            elif len(k) == 1:
                text = text + k[0]

if __name__ == "__main__":
    kc = KeyController()
    while True:
        
        k = kc.keypress()
        print(k)
        # control-C
        if k == CONTROL_C:
            break

        # function key
        if k[0] == '\x1b':
            fnum = 0
            for i,fkey in enumerate(FUNC_KEYS):
                if k == fkey:
                    fnum = i + 1
            if fnum:
                print("function key pressed F"+str(fnum))
        
        time.sleep(.1)