from cli_py2 import cli_ugs as UGS
from email_scanner import scan_email
from API_Files.image_gen import img_gen
from vectorize import vectorize_image

from icrawler.builtin import GoogleImageCrawler
import os
import sys
from pathlib import Path

import signal
from contextlib import contextmanager

import time

import subprocess

from threading import Thread
import functools

from time import time

from PIL import Image, ImageFilter

import matplotlib.pyplot as plt
from matplotlib.pyplot import plot, draw, show

import time

import cv2
import numpy as np
            
#request topic
out_file = ""
topic_fname = ""

def cnc_machine():
    #hardcode port for now
    port = 3
    topic = input("What shall we draw? ")
    #topic = None
    while topic == None:
        topic = scan_email()
        print("waiting")
        time.sleep(30)
    
    create_gcode(topic)
    UGS(out_file, port)
    
    
    
    #look at RA files, change it so that all images are gcoded and the smallest (0ver 1kb) file is moved to cnc

def create_gcode(topic):
    global out_file
    global topic_fname
    
    topic_fname = topic.replace(" ","_")
    out_file = "C:/Users/bfora/Desktop/cnc/" + topic_fname + ".nc"
    #check whether topic is already in cnc folder
    
    #remove existing 000001.png 
    
    if os.path.isfile(out_file) and os.stat(out_file).st_size > 1000:
        print("already done")
        return
    
    
    
    dir = "prints"

    
    
    for file in os.listdir(dir):
        filename = os.path.join(dir,file)
        try:
            os.remove(filename)
            print("removed")
        except OSError:
            print("not there")

    img_gen(topic)

    time.sleep(1)

    
    
    print(os.listdir(dir))

    if os.listdir(dir):
        for file in os.listdir(dir):
            print(file)
            filename = os.path.join(dir,file)
            im = Image.open(filename)
            im.save("prints/out.png")
            vectorize_image("prints/out.png", out_file, size = int(input("how big? ")))
            break
        
        return
    else:
        exit()



if __name__ == '__main__':
    cnc_machine()

