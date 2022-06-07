#!/usr/bin/python
# -*- coding:utf-8 -*-
import re

import configparser
import time


from keysconfig import *

import subprocess
from docmanager import DocManager

REFRESH_RATE = 8
CHAR_PER_LINE = 80
NB_HISTORY_LINES = 5
NB_MAX_LINES = 20
BACKUP_KEY = "/home/pi/.ssh/id_rsa"
BACKUP_DIR = "pi@192.168.1.2:/home/pi/piwrite"
KEYREADERPROG = "/home/pi/epd-writer/inkey"

class TestWriter():
    def __init__(self,fname) -> None:
        self.doc = DocManager("test")
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
        print(stattext)

    # get file content
    # returns an array of lines
    def getContent(self):
        content = []
        try:
            with open(self.fullpath) as f:
                content = f.readlines()
        except (FileNotFoundError, PermissionError, OSError):
            print("IO Error")

        return content

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
        print(f"gDC {startline}\n")
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

    def pwrite(self):
        tstart = time.time() - REFRESH_RATE
        tbegin = tstart
        fitcontent = []
        displaycontent = []
        # launch a separate process 
        # - read from keyboard
        # - write to file (self.fullpath)
        # - process stopped either by Ctl-C or Echap key
        #proc = subprocess.Popen([KEYREADERPROG,self.fullpath])
        
        startline = 0
        oldcontent = []
        while True:
            tcurrent = time.time()
            
            if tcurrent - tstart > REFRESH_RATE:
                # check if the inkey subprocess is still running
                #if proc.poll() is not None:
                #    print("poll exit")
                #    break
                # read the whole file
                filecontent = self.getContent()
                # adapt content to screen size
                fitcontent = self.getFitContent(filecontent)
                # only keep lines after startline
                filtercontent = fitcontent[startline:]
                if len(filtercontent) > NB_MAX_LINES:
                    startline = len(fitcontent) - NB_HISTORY_LINES
                    filtercontent = fitcontent[startline:]
                # only refresh if content has changed
                if filtercontent and oldcontent != filtercontent:
                
                    #self.displayStats(filecontent)
                    for i,line in enumerate(filtercontent):
                        print(f"{i}-{line}***")
                    oldcontent = filtercontent
                    
                tstart = time.time()
            if tcurrent - tbegin > 100:
                break
            time.sleep(.01)

    def write(self):
        print("READY To type ")
        # substract refresh rate so that we start drawing immediately
        tstart = time.time() - REFRESH_RATE
        tbegin = tstart

        displaycontent = []
        # launch a separate process 
        # - read from keyboard
        # - write to file (self.fullpath)
        # - process stopped either by Ctl-C or Echap key
        #proc = subprocess.Popen([KEYREADERPROG,self.fullpath])
        
        startline = 0
        oldcontent = []
        while True:
            tcurrent = time.time()
            
            if tcurrent - tstart > REFRESH_RATE:
                # check if the inkey subprocess is still running
                #if proc.poll() is not None:
                #    print("poll exit")
                #    break
                # read the whole file
                filecontent = self.getContent()
                # what should be displayed
                # we have a limited number of lines available on the screen
                displaycontent = self.getDisplayContent(filecontent,startline)
                print("\n------\n")
                print(displaycontent)
                print("\n------\n")
                endline = len(filecontent)
                if endline < NB_HISTORY_LINES:
                    startline = 0
                else:
                    startline = endline - len(displaycontent)
                    if startline < 0:
                        startline = 0
                # only refresh if content has changed
                if displaycontent and oldcontent != displaycontent:
                
                    #self.displayStats(filecontent)
                    for i,line in enumerate(displaycontent):
                        print(f"{i}-{line}***")
                    oldcontent = displaycontent
                    
                tstart = time.time()
            if tcurrent - tbegin > 100:
                print("TIME OUT !!!!")
                break
            time.sleep(.01)
        
if __name__ == "__main__":

    epdw = TestWriter("06-06-forloop.txt")
    epdw.pwrite()
    
    