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
from PIL import Image,ImageDraw,ImageFont
import traceback
from keypress import KeyController
from keysconfig import *
from threading import Thread
import subprocess
from docmanager import DocManager

REFRESH_RATE = 8
CHAR_PER_LINE = 80
NB_HISTORY_LINES = 5
NB_MAX_LINES = 20
BACKUP_KEY = "/home/pi/.ssh/id_rsa"
BACKUP_DIR = "pi@192.168.1.2:/home/pi/piwrite"
KEYREADERPROG = "/home/pi/epd-writer/inkey"

class EPDWriter(EPDPage):
    def __init__(self,fname) -> None:
        EPDPage.__init__(self)
        self.fname = fname
        self.fullpath = self.doc.getFullPath(fname)
        self.lastcontent = False
        # session word count
        self.stats = False
        self.wordcount = 0
        self.charactercount = 0
        self.startTime = time.time()
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

    # display statistics for text - word count, characters
    def displayStats(self,filecontent):
        # word count
        wc = 0
        # character count
        cc = 0
        for line in filecontent:
            wc = wc + len(re.findall(r'\w+',line))
            cc = cc + len(re.findall(r'.',line))
        # initialize word count for this writing session
        if self.stats is False:
            self.wordcount = wc
            self.charactercount = cc
            self.stats = True

        stattext = "total mots " + str(wc) + " - signes " +str(cc)+ " // session mots " + str(wc - self.wordcount)  + " - signes " +str(cc - self.charactercount)
        self.draw.text((160, 425), self.fname + " - " + self.getTimer(), font = self.font18, fill = 0)
        self.draw.text((160, 445), stattext, font = self.font18, fill = 0)

    # display elapsed time for this writing session
    def getTimer(self):
        current = time.time()
        duration = self.startTime - current
        if duration < 60:
            seconds = duration
            minutes = 0
            hours = 0
        elif duration < 3600:
            minutes = duration//60
            seconds = duration%60
            hours = 0
        else:
            hours = duration //3600
            remainder = duration % 3600
            if remainder > 60:
                minutes = remainder//60
                seconds = remainder % 60
            else:
                minutes = 0
                seconds = remainder
        strtime = '%02d:%02d:%02d' % (hours, minutes, seconds)
        return strtime

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

    def write(self):
        print("READY To type ")
        # substract refresh rate so that we start drawing immediately
        tstart = time.time() - REFRESH_RATE
        tbegin = tstart

        # launch a separate process 
        # - read from keyboard
        # - write to file (self.fullpath)
        # - process stopped either by Ctl-C or Echap key
        proc = subprocess.Popen([KEYREADERPROG,self.fullpath])
        self.displayMenu()
        self.display()
        startline = 0
        oldcontent = []
        self.startTime = time.time()
        while True:
            tcurrent = time.time()
            
            if tcurrent - tstart > REFRESH_RATE:
                # check if the inkey subprocess is still running
                if proc.poll() is not None:
                    print("inkey process exit")
                    break
                # read the whole file
                filecontent = self.getContent()
                # what should be displayed
                # we have a limited number of lines available on the screen
                # adapt content to screen size
                fitcontent = self.getFitContent(filecontent)
                # only keep lines after startline
                filtercontent = fitcontent[startline:]
                # we have too many lines to display
                if len(filtercontent) > NB_MAX_LINES:
                    # keep only a few lines to keep history of what was written
                    startline = len(fitcontent) - NB_HISTORY_LINES
                    filtercontent = fitcontent[startline:]
                
                # only refresh if content has changed
                if filtercontent and oldcontent != filtercontent:
                    self.clearImage()
                    self.displayMenu()
                    self.displayStats(filecontent)
                    for i,line in enumerate(filtercontent):
                        self.draw.text((10, 20*i), str(line), font = self.font18, fill = 0)

                    self.display()
                    oldcontent = filtercontent
                    
                tstart = time.time()

            time.sleep(.01)
        
        if self.enableBackup:
            print("starting backup")
            #backupProcess = subprocess.Popen(["scp","-i",BACKUP_KEY,self.fullpath,BACKUP_DIR])
            backupProcess = subprocess.Popen(["scp","-i",self.backupkey,self.fullpath,self.backupdir])
        else:
            print("backup disabled")
        
if __name__ == "__main__":

    epdw = EPDWriter("mytest")
    epdw.write()
    
    