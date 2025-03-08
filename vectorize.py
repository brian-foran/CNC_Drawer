import os
from pathlib import Path
from PIL import Image, ImageFilter
import matplotlib.pyplot as plt
from matplotlib.pyplot import plot, draw, show
import time
import cv2
import numpy as np
import copy
from math import sqrt

def monochrome(image_path):
    global img
    img = cv2.imread(image_path, 1)  # 0 for grayscale

    black = np.array([125,125,15])
    black_points = np.where([img < black][0], 1, 0)

    unique1, amt_black = np.unique(black_points, return_counts=True)
        
    perc_black = (amt_black[1]/sum(amt_black))
    print(perc_black)
    return perc_black

def get_outline_pixels(image_path):
    image = Image.open(image_path)
    image = image.convert(mode='RGB')
    image = image.filter(ImageFilter.FIND_EDGES)
    new_image_path = image_path.replace(".png", "_1.png").replace(".jpg", "_1.jpg")


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

    return x, y , coords

def get_pixels(image_path):
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

    return x, y, coords

def plot_xy(x, y):
    fig = plt.figure()
    ax = fig.add_subplot()
    plt.scatter(x, y, s = .1)
    ax.set_aspect('equal', adjustable='box')

    fig.set_figheight(20)
    plt.draw()

def generate_box_coords(n):
        #create an array of coordinates for a box of size n
        #this is the distances that the algorithm will look at to determine the next pixel
        box = []
        for x in range(-n, n+1):
            for y in range(-n, n+1):
                if abs(x) == n or abs(y) == n:
                    box.append((x, y))
        return box

def img_to_coords(image_path):
    #convert image to monochrome
    perc_black = monochrome(image_path)


    #get image pixels
    #if there is a lot of black, then the image is a sillouette and we can use the outline
    # convert to image outline, then extract pixels 
    #if perc_black > .05:
    if True:
        x, y, coords = get_outline_pixels(image_path)
        #for the time being, always use the outline
        
    #else, the image is already a line drawing
    # convert to pixels           
    else:
        x, y, coords = get_pixels(image_path)

    #plot the pixels
    plot_xy(x, y)

    return x, y, coords

def create_gcode_two_pens(vectors, out_file):
    g_code = []
    g_code.append("F40000\n")

    g_code.append("G92X0Y0\n")

    z_down = "z200\n"
    #to flip colors
    z_color2 = "z-200\n"
    z_up = "z0\n"
    color_flip = True

    #offset for different pens
    x_offset =  -300
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
    x_shift = -200

    for v in vectors:
        g_code.append(f"{z_up}")
        start = True
        for elem in v:
            elem[0], elem[1] = elem[1], elem[0]     #flip x and y
            if start:
                if color_flip:
                    z = z_down
                    #uncommnet to use both colors
                    color_flip = False
                    x_pos = elem[0] + x_offset + x_shift
                    
                else:
                    z = z_color2
                    color_flip = True
                    x_pos = elem[0] + x_shift
                    
                line = f'G0 X{x_pos*scale} Y{elem[1]*scale} {z_up} {z}'
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

    g_code.append("G0 z0\n")
    g_code.append("G0 X0 Y0\n")
    g_code.append("$H\n")

    with open(out_file, "w") as output:
        for line in g_code:
            output.write(line)

def create_gcode(vectors, out_file):
    g_code = []

    z_down = "G0 z400\n"
    #to flip colors
    z_up = "G0 z0\n"

    g_code.append("F100000\n")  #feedrate
    g_code.append(z_up)  #move up
    g_code.append("G04 P1\n")   #pause
    g_code.append("G92X0Y0\n")  #move to 0,0

    #gcode to move the roll of paper to make room for the next drawing
    g_code.append("M03\n")  
    g_code.append("G04 P4\n")
    g_code.append("M05\n")
    g_code.append("G04 P1\n")

    print("Brian")
    max_xy = 0
    min_x = 100000
    min_y = 100000
    for v in vectors:
        for coord in v:
            min_x = min(min_x, coord[1])
            min_y = min(min_y,coord[0])


    new_vectors = []

    for v in vectors:
        new_v = []
        for coord in v:
            #flip x and y and find max
            new_x = coord[1] - min_x
            new_y = coord[0] - min_y
            new_v.append((new_x, new_y))
            max_xy = max(max_xy, max(new_x, new_y))
        new_vectors.append(new_v)
    
    vectors = new_vectors

    max_dim = size_
    scale = max_dim/max_xy
    prev_line = ""

    #shift entire drawing
    #x_shift = max_dim*.8
    x_shift = 0

    for v in vectors:
        g_code.append(f"{z_up}")
        start = True
        for elem in v:
            if start:
                z = z_down
                x_pos = elem[0] + x_shift
                line = f'G0 X{x_pos*scale} Y{elem[1]*scale} \n {z_up} {z}'
                start = False

            else:
                x_pos = elem[0] + x_shift
                    
                line = f'G1 X{x_pos*scale} Y{elem[1]*scale} \n'

            if line != prev_line:
                g_code.append(line)
            prev_line = line

    g_code.append(z_up)
    g_code.append("G0 X-10 Y-10\n")

    with open(out_file, "w") as output:
        for line in g_code:
            output.write(line)

def plot_vectors(vectors):
    fig = plt.figure()
    ax = fig.add_subplot()
    print(f"vector length: {len(vectors)}")
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
    

def find_next_pixel(coords_, lim_x, lim_y, curr_x, curr_y, v1, min_jump, max_jump):
    end = True
    #look at the pixels in the box
    for k in range(min_jump, max_jump):
        box = boxes[k]
        for i in range(len(box)):
            new_x = curr_x + box[i][0]
            new_y = curr_y+ box[i][1]

            if new_x >= lim_x or new_y >= lim_y or new_x <0 or new_y <0:
                continue

            if coords_[new_x, new_y] == 1:
                v1.append((new_x, new_y))
                v1.append((new_x, new_y))
                end = False

            coords_[new_x, new_y] = 0
            
        if not end:
            break

    return coords_, v1, end

def coords_to_vectors(coords, min_vector_length):
    coords_ = copy.deepcopy(coords)
    global boxes 
    boxes = []
    for i in range(1,max_depth+1):
        boxes.append(generate_box_coords(i))

    closed_vectors = []
    vectors = []
    lim_x = len(coords_)
    lim_y = len(coords_[0])
    #start at first point in x,y then look at coords to see if there is a clockwise pixes

    #while there are still unvisited pixels
    while 1 in coords_:
        
        #create a new contiguous vector
        v1 = []
        #start at the next unvisited pixel
        x_arr, y_arr = np.where(coords_ == 1)
        
        start_x = x_arr[0]
        start_y = y_arr[0]

        #mark as visited
        coords_[start_x, start_y] = 0

        #add to the contiguous vector
        v1.append((start_x, start_y))
        end = False

        #while there are still unvisited pixels near the current pixel
        while not end:
            curr_x = v1[-1][0]
            curr_y = v1[-1][1]
            coords_, v1, end = find_next_pixel(coords_, lim_x, lim_y, curr_x, curr_y, v1, 0, z_hop_depth)
                
            if end:
                #if the vector is big enough to show up when drawing, then add to list
                if len(v1)> min_vector_length:
                    #print(len(v1))
                    #if the vec#tor ends near its initial point, then add to closed vectors
                    if v1 and sqrt((v1[0][0] - v1[-1][0])**2 + (v1[0][1] - v1[-1][1])**2) < max_depth:
                        closed_vectors.append(v1)

                    vectors.append(v1)
                    
                curr_x = v1[-1][0]
                curr_y = v1[-1][1]

                #reset the vector
                v1 = []
                    
                #this is to find the closes z-hop pixed, to minimize drawbot travel
                coords_, v1, end = find_next_pixel(coords_, lim_x, lim_y, curr_x, curr_y, v1, z_hop_depth, max_depth)
                #if no new pixels are found, start a new vector at the next unvisited pixel in coords
            
    return vectors, closed_vectors

def vectorize_image(image_path, out_file, size, min_vector_length = 20, max_depth_ = 100, z_hop_depth_ = 10):

    global max_depth
    global z_hop_depth
    global size_

    if size > 600:
        size = 600
        print("too large, setting size to 600")
    size_ = size


    max_depth = max_depth_
    z_hop_depth = z_hop_depth_

    time.sleep(1)
    
    x, y, coords = img_to_coords(image_path)

    #make array copies so that they can be modified
    vectors, closed_vectors = coords_to_vectors(coords, min_vector_length)
    
    

    plot_vectors(vectors)
    #plot_vectors(closed_vectors)
    #plt.show()

    create_gcode(vectors, out_file)    

if __name__ == '__main__':
    image_path = "prints/out.png"
    out_file = "C:/Users/bfora/Desktop/cnc/out.nc"
    #out_file = "test.nc"
    vectorize_image(image_path, out_file, 600)
    print("done")