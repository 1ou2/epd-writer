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
import subprocess
from docmanager import DocManager

REFRESH_RATE = 8

class EPDWriter(EPDPage):
    def __init__(self,fname) -> None:
        EPDPage.__init__(self)
        self.fname = fname
        self.fullpath = self.doc.getFullPath(fname)
    
    def displayMenu(self):
        # fill = 255 -> white
        # fill = 0 -> black
        self.draw.rectangle((10, 420, 140, 470), fill = 0)
        self.draw.text((20, 430), 'ECHAP ', font = self.font24, fill = 255)
        #self.draw.rectangle((160, 420, 300, 470), fill = 0)
        #self.draw.text((165, 430), 'F2 OPEN', font = self.font24, fill = 255)

    def startRecording(self):
        kc = KeyController()
        k = None
        while k != CONTROL_C or k !=F3:
            pass
    def write(self):
        print("READY To type ")
        tstart = time.time()
        tbegin = tstart
        text = ""
        lines = [""]
        lastrefresh = [""]
        currentline = 0
        proc = subprocess.Popen(["/home/pi/epd-writer/inkey",self.fullpath])
        self.displayMenu()
        self.display()
        
        line = 0
        col = 0
        while True:
            tcurrent = time.time()
            if tcurrent - tstart > REFRESH_RATE:
                if proc.poll() is not None:
                    print("poll exit")
                    break
                #self.clearImage()
                #self.displayMenu()
                
                self.draw.text((10+col*20, 20*line), str(line), font = self.font18, fill = 0)
                line = line +1
                self.display()
                    
                tstart = time.time()

            if line >= 20:
                print("Reset lines")
                line = 0
                col = col+1
            if tcurrent - tbegin > 60:
                break
            time.sleep(.01)

        
if __name__ == "__main__":

    epdw = EPDWriter("mytest")
    epdw.write()
    
    