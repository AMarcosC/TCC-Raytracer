import math
import numpy as np
from colour import Color
import pickle
from BasicFunctions import *
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

def color_range(n_colors):
    if n_colors == 1:
        return [Color("green")]
    elif n_colors == 2:
        return [Color("green"), Color("red")]
    elif n_colors == 3:
        return [Color("white"), Color("green"), Color("red")]
    elif n_colors == 4:
        return [Color("white"), Color("green"), Color("red"), Color("#581845")]
    elif n_colors >= 5:
        final_range = []
        color_division = distribute_for_two(n_colors)
        color0 = Color("blue")
        color1 = Color("yellow")
        range1 = list(color0.range_to(color1,color_division[0]+2))
        del range1[color_division[0]+1]
        del range1[color_division[0]]
        color2 = Color("red")
        range2 = list(color1.range_to(color2,color_division[1]+2))
        del range2[color_division[1]+1]
        del range2[color_division[1]]
        for c1 in range1:
            final_range.append(c1)
        for c2 in range2:
            final_range.append(c2)
        print(final_range)
        return final_range

def distribute_for_two(a):
    if a % 2 == 0:
        return [a//2, a//2]
    elif a % 2 == 1:
        return [(a//2)+1, a//2]

def color_range_image(list_colors):
    spacing = 50
    width = 3*spacing
    height = len(list_colors)*spacing
    image_m = np.full((height, width, 4), [255,255,255,255])
    cont = 0
    cont_n = 0
    for c in list_colors:
        for i in range(cont*spacing, (cont+1)*spacing, 1):
            for j in range(0, spacing, 1):
                image_m[i][j] = [c.red*255, c.green*255, c.blue*255, 255]
        cont = cont + 1
    img_color = Image.fromarray(np.uint8(image_m)).convert('RGBA')  #Transformando a matriz em uma imagem .png
    img0 = ImageDraw.Draw(img_color)
    myFont = ImageFont.truetype('utilities/Roboto-Black.ttf', 30)
    for c_n in list_colors:
        img0.text([60, (50*cont_n) + 10], "{}".format(cont_n), font=myFont, fill=(0,0,0))
        cont_n = cont_n + 1
    img_color.save('output/ColorDict.png')

def heatmap_to_img(h1,h2,h3,h4):
    numero_cores = int(abs(h1[0][0]) + abs(h2[0][0]) + abs(h3[0][0]) + abs(h4[0][0]) + 1)
    colors = color_range(numero_cores)
    soma = h1 + h2 + h3 + h4
    img = []
    for i in soma:
        line = []
        for j in i:
            if j >= 0:
                line.append([colors[int(j)].red*255,colors[int(j)].green*255,colors[int(j)].blue*255,255])
            else:
                line.append([0,0,0,0])
        img.append(line)
    img1 = Image.fromarray(np.uint8(img)).convert('RGBA')  #Transformando a matriz em uma imagem .png
    img1.save('output/Heatmap.png')
    color_range_image(colors)
    return soma

change_to_current_dir()

hea_1 = open('heatmap-20mar2022','rb')
heatmap_1 = pickle.load(hea_1)

hea_2 = open('heatmap-21jun2022','rb')
heatmap_2 = pickle.load(hea_2)

hea_3 = open('heatmap-22set2022','rb')
heatmap_3 = pickle.load(hea_3)

hea_4 = open('heatmap-21dez2022','rb')
heatmap_4 = pickle.load(hea_4)

heatmap_somado = heatmap_to_img(heatmap_1,heatmap_2,heatmap_3,heatmap_4)

python_array_to_pickle(heatmap_somado, 'heatmap-somado')
