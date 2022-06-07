#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os,subprocess

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

class EPDSplash(EPDPage):
    def __init__(self) -> None:
        EPDPage.__init__(self)

    def drawSplash(self):
        self.clearImage()
        self.draw.rectangle((10, 10, 140, 40), fill = 0)
        self.draw.text((20, 10), 'STARTED', font = self.font24, fill = 255)
        self.display()
        
if __name__ == "__main__":
    try:
        splash = EPDSplash()
        splash.drawSplash()
        splash.epd.sleep()
        epdconfig.module_exit()
        exit()
        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epdconfig.module_exit()
        exit()