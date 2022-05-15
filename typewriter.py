#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import logging
import epdconfig
from page import EPDPage
from waveshare import EPD

import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from keypress import KeyController
from keysconfig import *
from threading import Thread

REFRESH_RATE = 4

class EPDWriter(EPDPage):
    def __init__(self,fname) -> None:
        EPDPage.__init__(self)
        self.fname = fname
    
    def displayMenu(self):
        self.draw.rectangle((10, 420, 140, 470), fill = 0)
        # fill = 255 -> white
        self.draw.text((20, 430), 'F1 NEW', font = self.font24, fill = 255)
        self.draw.rectangle((160, 420, 300, 470), fill = 0)
        self.draw.text((165, 430), 'F2 OPEN', font = self.font24, fill = 255)

    def startRecording(self):
        kc = KeyController()
        k = None
        while k != CONTROL_C or k !=F3:
            pass
    def write(self):
        print("READY To type ")
        tstart = time.time()
        text = ""
        lines = [""]
        lastrefresh = [""]
        currentline = 0
        self.displayMenu()
        self.display()

        kc = KeyController()
        while True:
            k = kc.keypress()
            if k== CONTROL_C:
                break
            elif k == ENTER:
                currentline = currentline +1
                text = ""
                lines.append(text)
            elif k == BACKSPACE:
                while currentline >= 0:
                    text = lines[currentline]
                    if len(text) > 0:
                        text = text[:-1]
                        lines[currentline] = text
                        break
                    # line was empty go to previous line
                    else:
                        # we are in the first line with no text
                        if currentline == 0:
                            break
                        currentline = currentline - 1
                        # remove last element from list
                        del lines[-1]
            # user did not press any key 
            elif k == KEYTIMEOUT:                        
                pass
            elif len(k) == 1:
                text = text + k[0]
                lines[currentline] = text
                print(text)
                if len(text) > 80:
                    currentline = currentline+1
                    text = ""
                    lines.append(text)
                
            
            tcurrent = time.time()
            if tcurrent - tstart > REFRESH_RATE:
                print(lines)
                # only refresh if something has changed
                if lines != lastrefresh:
                    self.clearImage()
                    self.displayMenu()
                    for i,line in enumerate(lines):
                        self.draw.text((10, 20*i), line, font = self.font18, fill = 0)
                    self.display()
                    lastrefresh = lines.copy()
                tstart = time.time()

            if currentline >= 20:
                print("Reset lines")
                currentline = 0
                text = ""
                lines = [""]
            time.sleep(.01)

        time.sleep(1)
        self.epd.sleep()
        epdconfig.module_exit()
        exit()
        
if __name__ == "__main__":

    epdw = EPDWriter("mytest")
    epdw.write()
    
    