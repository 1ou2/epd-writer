#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')


import logging
import epdconfig
from waveshare import EPD

import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd7in5_V2 Demo "+picdir)
    #epd = epd7in5_V2.EPD()
    epd = EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

    # Drawing on the Horizontal image


    logging.info("3.read bmp file")
    Himage = Image.open(os.path.join(picdir, 'mountain.bmp'))
    draw = ImageDraw.Draw(Himage)
    draw.rectangle((10, 10, 140, 40), fill = 0)
    draw.text((20, 10), 'PRESS F9', font = font24, fill = 255)
    epd.display(epd.getbuffer(Himage))
    #time.sleep(2)
    """

    Himage = Image.open(os.path.join(picdir, 'plage.bmp'))
    draw = ImageDraw.Draw(Himage)
    draw.rectangle((10, 10, 140, 40), fill = 0)
    draw.text((20, 10), 'STARTED', font = font24, fill = 255)
    epd.display(epd.getbuffer(Himage))
    """
    
    #epd.init()
    #epd.Clear()

    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epdconfig.module_exit()
    exit()
