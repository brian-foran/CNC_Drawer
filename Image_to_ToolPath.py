from cli_py2 import cli_ugs as UGS
from email_scanner import scan_email
from image_gen import img_gen
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

import cv2
import numpy as np
from skimage.morphology import area_opening
            
#request topic
out_file = ""
topic_fname = ""

def cnc_machine():
    #hardcode port for now
    port = 5
    topic = input()
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
            vectorize(out_file)
            break
        
        return
    else:
        exit()


def vectorize(out_file):
    time.sleep(1)
    
    image_path = "prints/out.png"
    img = cv2.imread(image_path, 1)  # 0 for grayscale

    black = np.array([125,125,15])
    black_points = np.where([img < black][0], 1, 0)

    #white = np.array([125,125,125])
    #white_points = np.where(img >= white,1, 0)

    unique1, amt_black = np.unique(black_points, return_counts=True)
    #unique2, amt_white = np.unique(white_points, return_counts=True)
    #print(unique[0]/unique[1])
        
    perc_black = (amt_black[1]/sum(amt_black))
    print(perc_black)

    #print(amt_white[1]/sum(amt_white))


    # In[84]:


    if perc_black > .05:

        image = Image.open(image_path)
        image = image.convert(mode='RGB')
        image = image.filter(ImageFilter.FIND_EDGES)
        new_image_path = image_path.replace(".png", "_1.png")


        image.save(new_image_path) 
        
        time.sleep(1)
        
        print("reading")
        img = cv2.imread(new_image_path, 1)  # 0 for grayscale
        print("read")

        rows, cols, _= img.shape

        coords = np.zeros((rows, cols))
        x = []
        y = []
        
        print("start")
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                pixel_value = img[i, j]

                if pixel_value[0]>200:
                    coords[i,j] = 1
                    x.append(i)  
                    y.append(j)
                #elif pixel_value[0]>50:
                    #print(pixel_value)
                    
    else:
        rows, cols, _ = img.shape

        coords = np.zeros((rows, cols))
        x = []
        y = []

        for i in range(0, rows-1):
            for j in range(0, cols-1):
                pixel_value = img[i, j]

                if pixel_value[0]<=50:
                    coords[i,j] = 1
                    x.append(i)  
                    y.append(j)


    # In[85]:


    x = []
    y = []

    for i in range(1, rows-1):
        for j in range(1, cols-1):
            if coords[i,j] == 1:
                x.append(i)
                y.append(j)


    # In[86]:


    fig = plt.figure()
    ax = fig.add_subplot()
    plt.scatter(x, y, s = .1)
    ax.set_aspect('equal', adjustable='box')

    fig.set_figheight(20)
    plt.draw()


    # In[87]:


    def generate_box_coords(n):
        box = []
        for x in range(-n, n+1):
            for y in range(-n, n+1):
                if abs(x) == n or abs(y) == n:
                    box.append((x, y))
        return box


    # In[88]:


    boxes = []
    max_depth = 60
    z_hop_depth = 20
    for i in range(1,max_depth+1):
        boxes.append(generate_box_coords(i))




    # In[90]:


    import copy


    # In[91]:


    x_ = copy.deepcopy(x)
    y_ = copy.deepcopy(y)
    coords_ = copy.deepcopy(coords)

    x_arr, y_arr = np.where(coords_ == 1)
    #print(x_arr[0], y_arr[0])
    vectors = []
    lim_x = len(coords_)
    lim_y = len(coords_[0])

    #start at first point in x,y then look at coords to see if there is a clockwise pixes


    v1 = []
    while 1 in coords_:
        v1 = []
        x_arr, y_arr = np.where(coords_ == 1)
        
        start_x = x_arr[0]
        start_y = y_arr[0]
        coords_[start_x, start_y] = 0
        
        end = False
        v1.append((start_x, start_y))
        while not end:
            end = True
            curr_x = start_x
            curr_y = start_y
            for k in range(z_hop_depth):
                box = boxes[k]
                for i in range(len(box)):
                    new_x = curr_x + box[i][0]
                    new_y = curr_y+ box[i][1]

                    if new_x >= lim_x or new_y >= lim_y or new_x <0 or new_y <0:
                        continue

                    if coords_[new_x, new_y] == 1:
                        v1.append((new_x, new_y))
                        v1.append((new_x, new_y))
                        start_x = new_x
                        start_y = new_y
                        end = False

                    coords_[new_x, new_y] = 0
                    
                if not end:
                    break
                
            if end:
                if len(v1)>12:
                    print(len(v1))
                    vectors.append(v1)
                    
                v1 = []
                    
                    
                for k in range(z_hop_depth, max_depth):
                    box = boxes[k]
                    for i in range(len(box)):
                        new_x = curr_x + box[i][0]
                        new_y = curr_y+ box[i][1]

                        if new_x >= lim_x or new_y >= lim_y:
                            continue

                        if coords_[new_x, new_y] == 1:
                            start_x = new_x
                            start_y = new_y
                            end = False

                        coords_[new_x, new_y] = 0

                    if not end:
                        break
        
        
        
            


    # In[ ]:





    # In[92]:


    fig = plt.figure()
    ax = fig.add_subplot()
    colors = ["red", "orange", "yellow", "green", "blue", "purple", "black"]
    for i in range(len(vectors)):
        v0 = []
        v1 = []
        for elem in vectors[i]:
            v0.append(elem[1])
            v1.append(elem[0]*-1)
        
        #yhat = smooth(v1, 2)
        #ax.scatter(v0, yhat, s = .1, color = colors[i%len(colors)])
        ax.scatter(v0, v1, s = .1)


    ax.set_aspect('equal', adjustable='box')
        
    plt.xlim(0)
    plt.draw()
        


    # In[962]:


    #add function to include z jump within vector if box level required is too high


    g_code = []
    g_code.append("F40000\n")

    g_code.append("G92X0Y0\n")

    z_color1 = "Z200\n"
    #to flip colors
    z_color2 = "Z-200\n"
    z_up = "Z0\n"
    color_flip = True

    #offset for different pens
    x_offset =  400
    #x_offset = 0

    

    print("Brian")
    max_xy = 0
    for v in vectors:
        for coord in v:
            max_xy = max(max_xy, max(coord))

    max_xy += x_offset
    max_dim = 800
    scale = max_dim/max_xy
    prev_line = ""

    #shift entire drawing
    #x_shift = max_dim*.8
    x_shift = 0

    for v in vectors:
        g_code.append(f"G0 {z_up}")
        start = True
        for elem in v:
            if start:
                if color_flip:
                    z = z_color1
                    #uncommnet to use both colors
                    color_flip = False
                    x_pos = elem[0] + x_offset + x_shift
                    
                else:
                    z = z_color2
                    color_flip = True
                    x_pos = elem[0] + x_shift
                    
                line = f'G0 X{x_pos*scale} Y{elem[1]*scale} {z_up} G0 {z}'
                #color_flip = color_flip
                #print(color_flip)
                start = False
            else:
                if color_flip:
                    x_pos = elem[0] + x_shift
                else:
                    x_pos = elem[0] + x_offset + x_shift
                    
                line = f'G1 X{x_pos*scale} Y{elem[1]*scale} \n'

            if line != prev_line:
                g_code.append(line)
            prev_line = line

    g_code.append("G0 Z0\n")
    g_code.append("G0 X0 Y0\n")
    g_code.append("$H\n")
    # In[94]:


    #show()
    
    with open(out_file, "w") as output:
        for line in g_code:
            output.write(line)



if __name__ == '__main__':
    cnc_machine()

