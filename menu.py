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

class EPDMenu(EPDPage):
    def __init__(self) -> None:
        EPDPage.__init__(self)
        

    def drawPrompt(self,text=""):
        self.draw.text((160, 160), text+ " :", font = menu.font24, fill = 0)
        self.draw.rectangle((300, 160, 700, 200), outline=0)
        

    def drawMenu(self):
        self.draw.rectangle((10, 10, 140, 40), fill = 0)
        # fill = 255 -> white
        self.draw.text((20, 10), 'F1 NEW', font = self.font24, fill = 255)
        self.draw.rectangle((160, 10, 300, 40), fill = 0)
        self.draw.text((165, 10), 'F2 OPEN', font = self.font24, fill = 255)
        
if __name__ == "__main__":
    try:
        menu = EPDMenu()

        menu.draw.rectangle((10, 10, 140, 40), fill = 0)
        # fill = 255 -> white
        menu.draw.text((20, 10), 'F1 NEW', font = menu.font24, fill = 255)
        menu.draw.rectangle((160, 10, 300, 40), fill = 0)
        menu.draw.text((165, 10), 'F2 OPEN', font = menu.font24, fill = 255)
        menu.display()

        kc = KeyController()
        key = kc.waitKey([F1,F2])
        if key == F1:
            print("F1")
            menu.drawPrompt("Filename")
            menu.display()
            #kc.getText()
            print("READY To type ")
            tstart = time.time()
            text = ""
            lastrefresh = ""
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
                        menu.clearImage()
                        menu.drawMenu()
                        menu.drawPrompt("Filename")
                        menu.draw.text((310, 170), text, font = menu.font18, fill = 0)
                        menu.display()
                        lastrefresh = text
                    tstart = time.time()
                time.sleep(.01)

            epw = EPDWriter(text)
            epw.write()

        elif key == F2:
            menu.clearImage()
            menu.drawMenu()
            menu.drawPrompt("Filename")
            dm = DocManager()
            docs = dm.getDocs()
            for i,fname in enumerate(docs):
                menu.draw.text((50+i*20, 70), fname, font = menu.font18, fill = 0)
            menu.display()

        logging.info("Goto Sleep...")
        menu.epd.sleep()
        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epdconfig.module_exit()
        exit()