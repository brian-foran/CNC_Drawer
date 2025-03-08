from cli_py2 import cli_ugs as UGS
from record_v2 import CameraRecorder
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

import shutil
            
#request topic
out_file = ""
topic_fname = ""

def cnc_machine(topic, port):
    create_gcode(topic)

    #gcode is now created
    #start camera 
    recorder = CameraRecorder()
    video_file = recorder.output_file
    try:
        UGS(out_file, port)
    except:
        print("failed")
        return 0
    
    time.sleep(20)  #give the camera frames to linger on the final product
    recorder.stop_recording()

    if recorder.cap.isOpened():
        recorder.cap.release()
    if recorder.out.isOpened():
        recorder.out.release()
    cv2.destroyAllWindows()
    
    return video_file

def create_gcode(topic):
    global out_file
    global topic_fname
    
    topic_fname = topic.replace(" ","_")
    out_file = "C:/Users/bfora/Desktop/cnc/" + topic_fname + ".nc"


    #remove existing 000001.png     
    dir = "prints"
    
    for file in os.listdir(dir):
        filename = os.path.join(dir,file)
        try:
            os.remove(filename)
            print("removed")
        except OSError:
            print("not there")

    #check if the topic has already been generated
    image_file = "generated_images/" + topic + ".jpg"
    if os.path.exists(image_file):
        if not os.path.exists("prints"):
            raise ValueError("prints folder not found")
        shutil.copy(image_file, "prints/image.jpg")
    else:
        raise ValueError("Brian Test Failed")
        img_gen(topic)

    time.sleep(1)

    #vectorize the image
    print(os.listdir(dir))

    if os.listdir(dir):
        for file in os.listdir(dir):
            print(file)
            filename = os.path.join(dir,file)
            im = Image.open(filename)
            im.save("prints/out.png")
            vectorize_image("prints/out.png", out_file, size = 600)
            break
        
        return
    else:
        exit()



if __name__ == '__main__':
    cnc_machine(input(), 3)

