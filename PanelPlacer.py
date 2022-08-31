import numpy as np
import math
from BasicFunctions import *
from colour import Color
from PIL import Image

"""
Observações:

É desnecessário utilizar a matriz da área de interesse na locação, já que o mapa de calor só existe na área de interesse mesmo.
Porém ela pode ser utilizada para verificar a inclinação do telhado.

Próximos passos:
    - Alternar entre vertical e horizontal
    - Determinar eixos de implantação para executabilidade (placas alinhadas)
    - Testar várias ordens de colocação (outras heurísticas)
    - Considerar inclinação
    - Permitir a colocação de placas em áreas de sombreamento leve (usar < ou > em vez de =)
    - Permitir exportação da locação das placas (coordenadas)

"""

"""Classes"""


class Placa:  #classse que define as propriedades de um objeto genérico qualquer
    def __init__(self, id, coord):
        self.id = id
        self.color = random_color()
        self.coord = coord


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

def not_surrounded_by(array,i,j,value):
        if i == 0 or j == 0 or i == (len(array)-1) or j == (len(array[0])-1):  #evitar out of index
            return False
        elif (array[i-1][j-1] != value and
            array[i-1][j] != value and
            array[i-1][j+1] != value and
            array[i][j-1] != value and
            array[i][j+1] != value and
            array[i+1][j-1] != value and
            array[i+1][j] != value and
            array[i+1][j+1] != value):
            return True
        else:
            return False

def slope(p0, p1):
    dx = p1.x - p0.x
    dy = p1.y - p0.y
    dz = p1.z - p0.z
    dl = math.sqrt((dx**2) + (dy**2))
    return (abs(dz/dl))

def find_slope(ar):  #vai servir para o exemplo mas é muito arcaico, é melhor que esse valor venha do modelo
    for i in range (0, len(ar), 1):
        for j in range (0, len(ar[0])):
            if not_surrounded_by(ar, i, j, None):
                temp = 0
                if slope(ar[i][j-1], ar[i][j+1]) > temp:
                    temp = slope(ar[i][j-1], ar[i][j+1])
                elif slope(ar[i-1][j], ar[i+1][j]) > temp:
                    temp = slope(ar[i-1][j], ar[i+1][j])
                elif slope(ar[i-1][j-1], ar[i+1][j+1]) > temp:
                    temp = slope(ar[i-1][j-1], ar[i+1][j+1])
                elif slope(ar[i+1][j-1], ar[i-1][j+1]) > temp:
                    temp = slope(ar[i+1][j-1], ar[i-1][j+1])
                return temp


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
            placas_locadas[u][v] = placas_counter
    #for a in range (i-1-(panel_pix_x//2), i+1+(panel_pix_x//2), 1):
        #for b in range (i-1-(panel_pix_y//2), i+1+(panel_pix_y//2), 1):
            #print(placas_locadas[a][b])

def place_panels():
    global placas_counter
    for i in range(((panel_pix_y//2)+1), len(placas_locadas) - ((panel_pix_y//2)+1),1):
        for j in range(((panel_pix_x//2)+1),len(placas_locadas[0]) - ((panel_pix_x//2)+1),1):
            #print("Estamos no ponto {} {}".format(i,j))
            if placing_possible(i,j) == True:
                placas_counter += 1
                execute_placing(i,j)
                lista_placas.append(Placa(placas_counter, area_de_interesse[i][j]))
                print("---------------------------")
                print("Placa locada: eixo {} {}".format(i,j))
                print("---------------------------")
            else:   #apenas por motivos de debug
                where_looking[i][j] = 1
                continue

def return_placa_color(ident):
    for placa in lista_placas:
        if placa.id == ident:
            return placa.color

def placas_img():
    soma = placas_locadas
    img = []
    for i in soma:
        line = []
        for j in i:
            if j != None and j >= 0:
                line.append(return_placa_color(j))
            else:
                line.append([255,255,255,0])
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

incl = find_slope(area_de_interesse)
print("Inclinação: {}".format(incl))

file_heatmap = open('heatmap', 'rb')
heatmap = pickle.load(file_heatmap)


placas_locadas = np.full_like(area_de_interesse, None)
lista_placas = []
placas_counter = 0

where_looking = np.full_like(area_de_interesse, None)

pix_dim=pixel_size()

print(area_de_interesse.shape)
print(heatmap.shape)
print(placas_locadas.shape)

place_panels()
placas_img()

print(placas_locadas)
area_de_interesse_img()
where_looking_img()
overlay_images('output/Placas.png', 'output/Heatmap.png','output/placas_overlay.png')
