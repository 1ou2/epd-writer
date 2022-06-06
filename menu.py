#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

from writer import EPDWriter
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')


import logging
import epdconfig
from waveshare import EPD
from keypress import KeyController
from keysconfig import *
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from page import EPDPage
from docmanager import DocManager, Document

class EPDMenu(EPDPage):
    def __init__(self) -> None:
        EPDPage.__init__(self)
        

    def drawPrompt(self,text=""):
        self.draw.text((160, 160), text+ " :", font = menu.font24, fill = 0)
        self.draw.rectangle((300, 160, 700, 200), outline=0)
        

    def drawMenu(self):
        # fill = 0 -> black
        # fill = 255 -> white
        self.draw.rectangle((10, 10, 140, 40), fill = 0)
        self.draw.text((20, 10), 'F1 NEW', font = self.font24, fill = 255)
        self.draw.rectangle((160, 10, 300, 40), fill = 0)
        self.draw.text((165, 10), 'F2 OPEN', font = self.font24, fill = 255)
        self.draw.rectangle((310, 10, 450, 40), fill = 0)
        self.draw.text((315, 10), 'F3 EXIT', font = self.font24, fill = 255)
        self.draw.rectangle((470, 10, 620, 40), fill = 0)
        self.draw.text((475, 10), 'F4 HALT', font = self.font24, fill = 255)

    def onF1(self):
        print("F1")
        self.drawPrompt("Filename")
        self.display()
        
        print("READY To type ")
        tstart = time.time()
        text = ""
        lastrefresh = ""
        filename = input("enter filename\n")
        if filename:
            self.draw.text((310, 170), filename, font = self.font18, fill = 0)
            self.display()    
            epw = EPDWriter(filename)
            epw.write()
        self.onMainMenu()

    def backonF1(self):
        print("F1")
        self.drawPrompt("Filename")
        self.display()
        
        print("READY To type ")
        tstart = time.time()
        text = ""
        lastrefresh = ""
        kc = KeyController()
        while True:
            k = kc.keypress()
            if k== CONTROL_C:
                break
            elif k == ENTER:
                break
            elif k == BACKSPACE:
                
                if len(text) > 0:
                    text = text[:-1]
            # user did not press any key 
            elif k == KEYTIMEOUT:                        
                pass
            elif len(k) == 1:
                text = text + k[0]
                
            tcurrent = time.time()
            if tcurrent - tstart > 3:
                
                # only refresh if something has changed
                if text != lastrefresh:
                    self.clearImage()
                    self.drawMenu()
                    self.drawPrompt("Filename")
                    self.draw.text((310, 170), text, font = self.font18, fill = 0)
                    self.display()
                    lastrefresh = text
                tstart = time.time()
            time.sleep(.01)

        epw = EPDWriter(text)
        epw.write()

    def onF2(self):
        self.clearImage()
        self.drawMenu()
        #self.drawPrompt("Filename")
        dm = DocManager()
        docs = dm.getDocs()
        for i,fname in enumerate(docs):
            self.draw.text((50, 70+i*20), str(i) + " - " + fname, font = self.font18, fill = 0)
        self.display()
        kc = KeyController()
        while True:
            k = kc.keypress()
            # user did not press any key 
            if k == KEYTIMEOUT:                        
                pass
            elif len(k) == 1:
                print("opening file " + k[0])
                idoc = int(k[0])
                print("doc to open : " + docs[idoc])
                break
            time.sleep(.01)
        epw = EPDWriter(docs[int(k[0])])
        epw.write()
        self.onMainMenu()

    def onF3(self):
        # EXIT
        epdconfig.module_exit()
        exit()

    def onF4(self):
        epdconfig.module_exit()
        os.system("shutdown -h now")


    def onMainMenu(self):
        self.clearImage()
        self.drawMenu()
        self.display()
        kc = KeyController()
        key = kc.waitKey([F1,F2,F3,F4])
        if key == F1:
            self.onF1()
        elif key == F2:
            self.onF2()
        elif key == F3:
            self.onF3()
        elif key == F4:
            self.onF4()

if __name__ == "__main__":
    try:
        menu = EPDMenu()
        menu.onMainMenu()

        logging.info("Goto Sleep...")
        menu.epd.sleep()
        epdconfig.module_exit()
        exit()
        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epdconfig.module_exit()
        exit()