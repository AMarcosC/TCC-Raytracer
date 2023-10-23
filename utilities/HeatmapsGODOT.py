import math
import numpy as np
from colour import Color
import pickle
from BasicFunctions import *
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import csv


def color_range_default(n_colors):
	name = 'default'
	if n_colors == 1:
	    final_range = [Color("green")]
	elif n_colors == 2:
	    final_range = [Color("green"), Color("red")]
	elif n_colors == 3:
	    final_range = [Color("white"), Color("green"), Color("red")]
	elif n_colors == 4:
	    final_range = [Color("white"), Color("green"), Color("red"), Color("#581845")]
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
	return [final_range, name]


def color_range_grayscale(n_colors):
	name = 'grayscale'
	if n_colors == 1:
	    color = [Color("white")]
	elif n_colors == 2:
	    color = [Color("white"), Color("black")]
	elif n_colors >= 3:
	    color0 = Color("white")
	    color1 = Color("black")
	    color = list(color0.range_to(color1,n_colors+1))
	return [color, name]


def color_range_grayscale_intense(n_colors):
	name = 'grayscale-intense'
	if n_colors == 1:
	    final_range = [Color("white")]
	elif n_colors == 2:
	    final_range = [Color("white"), Color("black")]
	elif n_colors == 3:
	    final_range = [Color("white"), Color("gray"), Color("black")]
	elif n_colors >= 4:
	    final_range = []
	    color_range_1 = 4
	    color_range_2 = n_colors - 3
	    color0 = Color("white")
	    color1 = Color("gray")
	    range1 = list(color0.range_to(color1,color_range_1+2))
	    del range1[color_range_1+1]
	    del range1[color_range_1]
	    color2 = Color("black")
	    range2 = list(color1.range_to(color2,color_range_2+2))
	    del range2[color_range_2+1]
	    del range2[color_range_2]
	    for c1 in range1:
	        final_range.append(c1)
	    for c2 in range2:
	        final_range.append(c2)
	return [final_range, name]


def color_range_rainbow_ss(n_colors):
	name = 'rainbow-ss'
	if n_colors == 1:
	    color = [Color("#FCD697")]
	elif n_colors == 2:
	    color = [Color("#FCD697"), Color("#821E70")]
	elif n_colors >= 3:
	    color0 = Color("#FCD697")
	    color1 = Color("#821E70")
	    color = list(color0.range_to(color1,n_colors+1))
	return [color, name]


def color_range_sunsetdark(n_colors):
	name = 'sunset-dark'
	if n_colors == 1:
	    final_range = [Color("#FCDB9A")]
	elif n_colors == 2:
	    final_range = [Color("#FCDB9A"), Color("#821E70")]
	elif n_colors == 3:
	    final_range = [Color("#FCDB9A"), Color("#E6566F"), Color("#821E70")]
	elif n_colors >= 4:
	    final_range = []
	    color_division = distribute_for_two(n_colors)
	    color0 = Color("#FCDB9A")
	    color1 = Color("#E6566F")
	    range1 = list(color0.range_to(color1,color_division[0]+2))
	    del range1[color_division[0]+1]
	    del range1[color_division[0]]
	    color2 = Color("#821E70")
	    range2 = list(color1.range_to(color2,color_division[1]+2))
	    del range2[color_division[1]+1]
	    del range2[color_division[1]]
	    for c1 in range1:
	        final_range.append(c1)
	    for c2 in range2:
	        final_range.append(c2)
	return [final_range, name]


def color_range_mint(n_colors):
	name = 'mint'
	if n_colors == 1:
	    range1 = [Color("white")]
	elif n_colors == 2:
	    range1 = [Color("white"), Color("#0F5A60")]
	elif n_colors >= 3:
	    color0 = Color("white")
	    color1 = Color("#0F5A60")
	    range1 = list(color0.range_to(color1,n_colors+1))
	return [range1, name]

def color_range_mint_intense(n_colors):
	name = 'mint-intense'
	if n_colors == 1:
	    final_range = [Color("white")]
	elif n_colors == 2:
	    final_range = [Color("white"), Color("#0F5A60")]
	elif n_colors == 3:
	    final_range = [Color("white"), Color("#89C0B6"), Color("#0F5A60")]
	elif n_colors >= 4:
	    final_range = []
	    color_range_1 = 4
	    color_range_2 = n_colors - 3
	    color0 = Color("white")
	    color1 = Color("#89C0B6")
	    range1 = list(color0.range_to(color1,color_range_1+2))
	    del range1[color_range_1+1]
	    del range1[color_range_1]
	    color2 = Color("#0F5A60")
	    range2 = list(color1.range_to(color2,color_range_2+2))
	    del range2[color_range_2+1]
	    del range2[color_range_2]
	    for c1 in range1:
	        final_range.append(c1)
	    for c2 in range2:
	        final_range.append(c2)
	return [final_range, name]


def color_range_red(n_colors):
	name = 'red'
	if n_colors == 1:
	    range1 = [Color("white")]
	elif n_colors == 2:
	    range1 = [Color("white"), Color("red")]
	elif n_colors >= 3:
	    color0 = Color("white")
	    color1 = Color("red")
	    range1 = list(color0.range_to(color1,n_colors+1))
	return [range1, name]

def color_range_red_intense(n_colors):
	name = 'red-intense'
	if n_colors == 1:
	    final_range = [Color("white")]
	elif n_colors == 2:
	    final_range = [Color("white"), Color("red")]
	elif n_colors == 3:
	    final_range = [Color("white"), Color("#FB7252"), Color("red")]
	elif n_colors >= 4:
	    final_range = []
	    color_range_1 = 4
	    color_range_2 = n_colors - 3
	    color0 = Color("white")
	    color1 = Color("#FB7252")
	    range1 = list(color0.range_to(color1,color_range_1+2))
	    del range1[color_range_1+1]
	    del range1[color_range_1]
	    color2 = Color("red")
	    range2 = list(color1.range_to(color2,color_range_2+2))
	    del range2[color_range_2+1]
	    del range2[color_range_2]
	    for c1 in range1:
	        final_range.append(c1)
	    for c2 in range2:
	        final_range.append(c2)
	return [final_range, name]


def color_range_brown(n_colors):
	name = 'brown'
	if n_colors == 1:
	    range1 = [Color("#EDE5CF")]
	elif n_colors == 2:
	    range1 = [Color("#EDE5CF"), Color("brown")]
	elif n_colors >= 3:
	    color0 = Color("#EDE5CF")
	    color1 = Color("brown")
	    range1 = list(color0.range_to(color1,n_colors+1))
	return [range1, name]

def color_range_inferno(n_colors):
	name = 'inferno'
	if n_colors == 1:
	    final_range = [Color("#FAEA75")]
	elif n_colors == 2:
	    final_range = [Color("#FAEA75"), Color("red")]
	elif n_colors == 3:
	    final_range = [Color("#FAEA75"), Color("red"), Color("purple")]
	elif n_colors >= 4:
	    final_range = []
	    color_range_1 = 4
	    color_range_2 = n_colors - 3
	    color0 = Color("#FAEA75")
	    color1 = Color("red")
	    range1 = list(color0.range_to(color1,color_range_1+2))
	    del range1[color_range_1+1]
	    del range1[color_range_1]
	    color2 = Color("purple")
	    range2 = list(color1.range_to(color2,color_range_2+2))
	    del range2[color_range_2+1]
	    del range2[color_range_2]
	    for c1 in range1:
	        final_range.append(c1)
	    for c2 in range2:
	        final_range.append(c2)
	return [final_range, name]



def color_range(n_colors):
	name = 'default'
	if n_colors == 1:
	    final_range = [Color("green")]
	elif n_colors == 2:
	    final_range = [Color("green"), Color("red")]
	elif n_colors == 3:
	    final_range = [Color("white"), Color("green"), Color("red")]
	elif n_colors == 4:
	    final_range = [Color("white"), Color("green"), Color("red"), Color("#581845")]
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
	return [final_range, name]

def distribute_for_two(a):
    if a % 2 == 0:
        return [a//2, a//2]
    elif a % 2 == 1:
        return [(a//2)+1, a//2]

def color_range_image(list_colors):
	name = list_colors[1]
	spacing = 50
	width = 3*spacing
	height = len(list_colors[0])*spacing
	image_m = np.full((height, width, 4), [255,255,255,255])
	cont = 0
	cont_n = 0
	for c in list_colors[0]:
	    for i in range(cont*spacing, (cont+1)*spacing, 1):
	        for j in range(0, spacing, 1):
	            image_m[i][j] = [c.red*255, c.green*255, c.blue*255, 255]
	    cont = cont + 1
	img_color = Image.fromarray(np.uint8(image_m)).convert('RGBA')  #Transformando a matriz em uma imagem .png
	img0 = ImageDraw.Draw(img_color)
	myFont = ImageFont.truetype('Roboto-Black.ttf', 30)
	for c_n in list_colors[0]:
	    img0.text([60, (50*cont_n) + 10], "{}".format(cont_n), font=myFont, fill=(0,0,0))
	    cont_n = cont_n + 1
	img_color.save('output/ColorDict_{}.png'.format(name))

def heatmap_to_img(h1):   #colocar aqui
    numero_cores = int(abs(h1[0][0])) + 1  #somar aqui
    colors = color_range_brown(numero_cores)
    print(len(colors[0]))
    soma = h1  #somar aqui
    img = []
    for i in soma:
        line = []
        for j in i:
            if j >= 0:
                line.append([colors[0][int(j)].red*255,colors[0][int(j)].green*255,colors[0][int(j)].blue*255,255])
            else:
                line.append([0,0,0,0])
        img.append(line)
    img1 = Image.fromarray(np.uint8(img)).convert('RGBA')  #Transformando a matriz em uma imagem .png
    img1.save('output/Heatmap_{}.png'.format(colors[1]))
    color_range_image(colors)
    return soma

change_to_current_dir()

hea_1 = open('heatmap','rb')
heatmap_1 = pickle.load(hea_1)

#hea_2 = open('heatmap-21jun2022','rb')
#heatmap_2 = pickle.load(hea_2)

#hea_3 = open('heatmap2','rb')
#heatmap_3 = pickle.load(hea_3)

#hea_4 = open('heatmap-21dez2022','rb')
#heatmap_4 = pickle.load(hea_4)

heatmap_somado = heatmap_to_img(heatmap_1)  #somar aqui

python_array_to_pickle(heatmap_somado, 'heatmap-somado')
