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
CHAR_PER_LINE = 60
NB_HISTORY_LINES = 5
NB_MAX_LINES = 20

class EPDWriter(EPDPage):
    def __init__(self,fname) -> None:
        EPDPage.__init__(self)
        self.fname = fname
        self.fullpath = self.doc.getFullPath(fname)
        self.lastcontent = False

    def displayMenu(self):
        # fill = 255 -> white
        # fill = 0 -> black
        self.draw.rectangle((10, 420, 140, 470), fill = 0)
        self.draw.text((20, 430), 'ECHAP ', font = self.font24, fill = 255)
        #self.draw.rectangle((160, 420, 300, 470), fill = 0)
        #self.draw.text((165, 430), 'F2 OPEN', font = self.font24, fill = 255)

    def getContent(self):
        content = []
        try:
            with open(self.fullpath) as f:
                content = f.readlines()
        except (FileNotFoundError, PermissionError, OSError):
            print("IO Error")

        return content

    # content : a list of lines - the full file
    # startline : starting line to use for the display
    def getDisplayContent(self,content,startline):
        displaycontent = content[startline:]
        # fit lines to max size
        fitcontent = []
        for line in displaycontent:
            if len(line) <= CHAR_PER_LINE:
                fitcontent.append(license)
            else:
                
                for i in range(0,len(line),CHAR_PER_LINE):
                    fitcontent.append(line[i:i+CHAR_PER_LINE])
                if i+CHAR_PER_LINE < len(line):
                    fitcontent.append(line[i+CHAR_PER_LINE:len(line)])
        if len(fitcontent) < NB_MAX_LINES:
            return fitcontent
        else:
            return fitcontent[-NB_HISTORY_LINES]

    def write(self):
        print("READY To type ")
        tstart = time.time()
        tbegin = tstart

        filecontent = self.getContent()
        
        displaycontent = []
        for line in reversed(filecontent):
            if len(line) <= CHAR_PER_LINE:
                displaycontent.insert(0,line)
            # line is too long truncate it
            else:
                displaycontent.insert(0,line[-CHAR_PER_LINE:])
                break
        # only keep the last lines to display
        if len(displaycontent) > NB_HISTORY_LINES:
            displaycontent = displaycontent[0:NB_HISTORY_LINES]

        endline = len(filecontent)
        startline = endline - len(displaycontent)
        text = ""
        lines = [""]
        lastrefresh = [""]
        currentline = 0
        proc = subprocess.Popen(["/home/pi/epd-writer/inkey",self.fullpath])
        self.displayMenu()
        for i,line in enumerate(displaycontent):
            self.draw.text((10, 20*i), str(line), font = self.font18, fill = 0)
        self.display()
        
       
        while True:
            tcurrent = time.time()
            if tcurrent - tstart > REFRESH_RATE:
                if proc.poll() is not None:
                    print("poll exit")
                    break
                filecontent = self.getContent()
                newend= len(filecontent)
                # we have more lines to display
                if newend > endline:
                    displaycontent = self.getDisplayContent(filecontent,startline)

                if displaycontent:
                    self.clearImage()
                    self.displayMenu()
                    for i,line in enumerate(displaycontent):
                        self.draw.text((10, 20*i), str(line), font = self.font18, fill = 0)

                    self.display()
                    
                tstart = time.time()

            if tcurrent - tbegin > 60:
                break
            time.sleep(.01)

        
if __name__ == "__main__":

    epdw = EPDWriter("mytest")
    epdw.write()
    
    