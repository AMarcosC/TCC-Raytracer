import numpy as np
import math
from BasicFunctions import *
from colour import Color
from PIL import Image

"""
Observações:

É desnecessário utilizar a matriz da área de interesse na locação, já que o mapa de calor só existe na área de interesse mesmo.
Porém ela pode ser utilizada para verificar a inclinação do telhado.

"""

"""Funções"""

def pixel_size():
    for i in range (0 , len(area_de_interesse)):
        for j in range (0, len(area_de_interesse[0])):
            if area_de_interesse[i][j] != None and area_de_interesse[i+1][j+1] != None:
                x0 = area_de_interesse[i][j].x
                y0 = area_de_interesse[i][j].y
                x1 = area_de_interesse[i+1][j+1].x
                y1 = area_de_interesse[i+1][j+1].y
                pix_x = abs(x1 - x0)
                pix_y = abs(y1 - y0)
                pix_area = pix_x * pix_y
                print("Altura do pixel: {}".format(pix_y))
                print("Largura do pixel: {}".format(pix_x))
                print("Área do pixel: {}".format(pix_area))
                return(pix_x,pix_y)

#def panel_pixel_size():

def placing_possible(i,j):
    #print("I atual: {}".format(i))
    #print("J atual: {}".format(j))
    temp_list = []
    for u in range (i-(panel_pix_y//2), i+(panel_pix_y//2), 1):
        for v in range (j-(panel_pix_x//2), j+(panel_pix_x//2), 1):
            if (placas_locadas[u][v] == None and
            heatmap[u][v] == 0 #and
            #area_de_interesse[u][v] != None
            ):
                temp_list.append(True)
            else:
                temp_list.append(False)
    for value in temp_list:
        if value == False:
            return False
    return True


def execute_placing(i,j):
    for u in range (i-(panel_pix_y//2), i+(panel_pix_y//2), 1):
        for v in range (j-(panel_pix_x//2), j+(panel_pix_x//2), 1):
            placas_locadas[u][v] = 1
    #for a in range (i-1-(panel_pix_x//2), i+1+(panel_pix_x//2), 1):
        #for b in range (i-1-(panel_pix_y//2), i+1+(panel_pix_y//2), 1):
            #print(placas_locadas[a][b])

def place_panels():
    for i in range(((panel_pix_y//2)+1), len(placas_locadas) - ((panel_pix_y//2)+1),1):
        for j in range(((panel_pix_x//2)+1),len(placas_locadas[0]) - ((panel_pix_x//2)+1),1):
            #print("Estamos no ponto {} {}".format(i,j))
            if placing_possible(i,j) == True:
                execute_placing(i,j)
                print("---------------------------")
                print("Placa locada: eixo {} {}".format(i,j))
                print("---------------------------")
            else:
                where_looking[i][j] = 1
                continue


def heatmap_to_img():
    initial_color = Color("blue")
    soma = placas_locadas
    img = []
    for i in soma:
        line = []
        for j in i:
            if j != None and j >= 0:
                line.append([0,0,255,255])
            else:
                line.append([255,255,255,255])
        img.append(line)
    img1 = Image.fromarray(np.uint8(img)).convert('RGBA')  #Transformando a matriz em uma imagem .png
    img1.save('output/Placas.png')
    return soma


def area_de_interesse_img():  #apenas para debug
    soma = area_de_interesse
    img = []
    for i in soma:
        line = []
        for j in i:
            if j != None:
                line.append([111,111,111,255])
            else:
                line.append([255,255,255,255])
        img.append(line)
    img1 = Image.fromarray(np.uint8(img)).convert('RGBA')  #Transformando a matriz em uma imagem .png
    img1.save('output/Area.png')
    return soma


def where_looking_img():  #apenas para debug
    soma = where_looking
    img = []
    for i in soma:
        line = []
        for j in i:
            if j != None:
                line.append([10,200,10,255])
            else:
                line.append([255,255,255,255])
        img.append(line)
    img1 = Image.fromarray(np.uint8(img)).convert('RGBA')  #Transformando a matriz em uma imagem .png
    img1.save('output/Loop_debug.png')
    return soma


"""Variáveis Globais"""
pix_x = None
pix_y = None
pix_area = None

panel_pix_x = 11  #trocar depois nas funções
panel_pix_y = 21



"""Inicialização"""

file_area = open('area', 'rb')
area_de_interesse = pickle.load(file_area)


file_heatmap = open('heatmap', 'rb')
heatmap = pickle.load(file_heatmap)


placas_locadas = np.full_like(area_de_interesse, None)

where_looking = np.full_like(area_de_interesse, None)

pix_dim=pixel_size()

print(area_de_interesse.shape)
print(heatmap.shape)
print(placas_locadas.shape)

place_panels()
heatmap_to_img()

print(placas_locadas)
area_de_interesse_img()
where_looking_img()
