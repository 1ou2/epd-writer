#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')


import logging
import epdconfig
from waveshare import EPD
from keypress import KeyController
from keysconfig import *
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from docmanager import DocManager

class EPDPage:
    def __init__(self) -> None:
        logging.basicConfig(level=logging.DEBUG)
        logging.info("PAGE")
        self.epd = EPD()
        logging.info("init and Clear")
        self.epd.init()
        self.epd.Clear()
        self.font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        self.font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
        self.image = Image.new('1', (self.epd.width, self.epd.height), 255)  # 255: clear the frame
        self.draw = ImageDraw.Draw(self.image)
        self.doc = DocManager()
        
    def clearImage(self):
        self.image = Image.new('1', (self.epd.width, self.epd.height), 255)  # 255: clear the frame
        self.draw = ImageDraw.Draw(self.image)

    def display(self):
        self.epd.display(self.epd.getbuffer(self.image))