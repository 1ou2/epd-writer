#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys,re
import os
import logging
import epdconfig
from page import EPDPage
from waveshare import EPD
import configparser
import time
#from PIL import Image,ImageDraw,ImageFont
import traceback
from keypress import KeyController
from keysconfig import *
from threading import Thread
import subprocess
from docmanager import DocManager
import math

REFRESH_RATE = 8
CHAR_PER_LINE = 80
NB_HISTORY_LINES = 5
NB_MAX_LINES = 20
BACKUP_KEY = "/home/pi/.ssh/id_rsa"
BACKUP_DIR = "pi@192.168.1.2:/home/pi/piwrite"
KEYREADERPROG = "/home/pi/epd-writer/arrowkeys"

class EPDReader(EPDPage):
    def __init__(self,fname) -> None:
        EPDPage.__init__(self)
        self.fname = fname
        self.fullpath = self.doc.getFullPath(fname)
        self.lastcontent = False
        # session word count
        self.stats = False
        self.wordcount = 0
        self.charactercount = 0
        self.getConfig()

    def getConfig(self):
        # enable backup
        config = configparser.ConfigParser()
        config.read("settings.ini")
        if config["Backup"]["enable"] == "yes":
            self.enableBackup = True
            self.backupkey = config["Backup"]["key"]
            self.backupdir = config["Backup"]["remotedir"]
        else:
            self.enableBackup = False

    def displayMenu(self):
        # fill = 255 -> white
        # fill = 0 -> black
        self.draw.rectangle((10, 420, 140, 470), fill = 0)
        self.draw.text((20, 430), 'ECHAP ', font = self.font24, fill = 255)
        self.draw.rectangle((160, 420, 200, 470), fill = 0)
        self.draw.text((160, 430), ' -> ', font = self.font24, fill = 255)
        self.draw.rectangle((250, 420, 320, 470), fill = 0)
        self.draw.text((250, 430), ' <- ', font = self.font24, fill = 255)

    # returns the index of the page to display
    # reads input.arrow file where 
    # + means next page 
    # - means previous page
    # so ++-, means next + next + previous -> next page
    #
    # lastpage : index of the last page
    # returns a number between 0..lastpage
    def getPage(self,lastpage):
        content = []
        try:
            with open("input.arrow") as f:
                content = f.readlines()
        except (FileNotFoundError, PermissionError, OSError):
            print("IO Error")
        page = 0
        for line in content:
            for c in line:
                if c == "+" and page < lastpage:
                    page = page +1
                if c == "-" and page > 0:
                    page = page -1
        return page

    def getContent(self):
        content = []
        try:
            with open(self.fullpath) as f:
                content = f.readlines()
        except (FileNotFoundError, PermissionError, OSError):
            print("IO Error")

        return content

    # adapt content to dispaly
    # returns an array of lines 
    def getFitContent(self,content):
        # fit lines to max size
        fitcontent = []
        for line in content:
            if len(line) <= CHAR_PER_LINE:
                fitcontent.append(line)
            else:
                for i in range(0,len(line),CHAR_PER_LINE):
                    fitcontent.append(line[i:i+CHAR_PER_LINE])
                if i+CHAR_PER_LINE < len(line):
                    fitcontent.append(line[i+CHAR_PER_LINE:len(line)])
        return fitcontent

    # content : a list of lines - the full file
    # startline : starting line to use for the display
    def getDisplayContent(self,content,startline):
        print("gDC ",startline)
        #print(content)
        displaycontent = content[startline:]
        # fit lines to max size
        fitcontent = []
        for line in displaycontent:
            if len(line) <= CHAR_PER_LINE:
                fitcontent.append(line)
            else:
                for i in range(0,len(line),CHAR_PER_LINE):
                    fitcontent.append(line[i:i+CHAR_PER_LINE])
                if i+CHAR_PER_LINE < len(line):
                    fitcontent.append(line[i+CHAR_PER_LINE:len(line)])
        if len(fitcontent) < NB_MAX_LINES:
            return fitcontent
        else:
            return fitcontent[-NB_HISTORY_LINES:]

    def read(self):
        print("READY To type ")
        # substract refresh rate so that we start drawing immediately
        tstart = time.time() - REFRESH_RATE
        tbegin = tstart

        # launch a separate process 
        # - read from keyboard
        # - write to file (input.arrow)
        # - process stopped either by Ctl-C or ESC + ESC key
        proc = subprocess.Popen([KEYREADERPROG])
        self.displayMenu()
        self.display()

        # read the whole file
        filecontent = self.getContent()
        # what should be displayed
        # we have a limited number of lines available on the screen
        # adapt content to screen size
        fitcontent = self.getFitContent(filecontent)

        lastpage = int(math.trunc(len(fitcontent)/NB_MAX_LINES))
        totallen = len(fitcontent)
        print(f"last page: {lastpage} - totallen {totallen}")
        startline = 0
        oldpage = -1
        while True:
            # check if keyboard arrow program has exited
            if proc.poll() is not None:
                    print("poll exit")
                    break
            page = self.getPage(lastpage)
            if page >= lastpage:
                page = lastpage
                startline = page * NB_MAX_LINES
                filtercontent = fitcontent[startline:len(fitcontent)]
            
            else:
                startline = page * NB_MAX_LINES
                filtercontent = fitcontent[startline:startline+NB_MAX_LINES]

            # new page to display
            if page != oldpage:
                print(f"display page from {oldpage} to {page}")
                oldpage = page
                
                self.clearImage()
                self.displayMenu()
                
                for i,line in enumerate(filtercontent):
                    self.draw.text((10, 20*i), str(line), font = self.font18, fill = 0)

                self.display()

            time.sleep(.1)
        
        
if __name__ == "__main__":

    epdr = EPDReader("mytest")
    epdr.read()
    
    