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
    global pix_x, pix_y, pix_area, area_de_interesse
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
                or_temp = None
                if slope(ar[i][j-1], ar[i][j+1]) > temp:
                    temp = slope(ar[i][j-1], ar[i][j+1])
                    or_temp = 'x'
                elif slope(ar[i-1][j], ar[i+1][j]) > temp:
                    temp = slope(ar[i-1][j], ar[i+1][j])
                    or_temp = 'y'
                elif slope(ar[i-1][j-1], ar[i+1][j+1]) > temp:
                    temp = slope(ar[i-1][j-1], ar[i+1][j+1])
                    or_temp = 'other'
                elif slope(ar[i+1][j-1], ar[i-1][j+1]) > temp:
                    temp = slope(ar[i+1][j-1], ar[i-1][j+1])
                    or_temp = 'other'
                return (temp, or_temp)

def placa_projection():
    global placa_dim1, placa_dim2, placa_dimx, placa_dimy
    alpha = math.cos(math.atan(incl[0]))
    print(alpha)
    if orient == 'Vert' and incl[1] == 'x':
        placa_dimx = menor(placa_dim1, placa_dim2) * alpha
        placa_dimy = maior(placa_dim1, placa_dim2)
    elif orient == 'Vert' and incl[1] == 'y':
        placa_dimx = menor(placa_dim1, placa_dim2)
        placa_dimy = maior(placa_dim1, placa_dim2) * alpha
    elif orient =='Hor' and incl[1] == 'x':
        placa_dimx = maior(placa_dim1, placa_dim2) * alpha
        placa_dimy = menor(placa_dim1, placa_dim2)
    elif orient =='Hor' and incl[1] == 'y':
        placa_dimx = maior(placa_dim1, placa_dim2)
        placa_dimy = menor(placa_dim1, placa_dim2) * alpha

"""
#esta versão da função garante que o número de pixels da placa
#será impar, importante para locar no eixo

def dimention_to_pixel():
    global panel_pix_x, panel_pix_y
    temp_x = (placa_dimx//round(pix_x,4)) + 1
    temp_y = (placa_dimy//round(pix_y,4)) + 1
    if impar(temp_x) == True:
        panel_pix_x = int(temp_x)
    else:
        panel_pix_x = int(temp_x+1)
    if impar(temp_y) == True:
        panel_pix_y = int(temp_y)
    else:
        panel_pix_y = int(temp_y+1)
    print("Placa terá {} px em X e {} px em Y".format(panel_pix_x,panel_pix_y))
    print("O tamanho real será de {} m em X e {} m em Y".format(panel_pix_x*round(pix_x,4),panel_pix_y*round(pix_y,4)))
"""

def dimention_to_pixel():
    global panel_pix_x, panel_pix_y
    temp_x = (placa_dimx//round(pix_x,4)) + 1
    temp_y = (placa_dimy//round(pix_y,4)) + 1
    panel_pix_x = int(temp_x)
    panel_pix_y = int(temp_y)
    print("Placa terá {} px em X e {} px em Y".format(panel_pix_x,panel_pix_y))
    print("O tamanho real será de {} m em X e {} m em Y".format(panel_pix_x*round(pix_x,4),panel_pix_y*round(pix_y,4)))

"""
#funções que colocam as placas no eixo (dimensões ímpares em pixels)

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
"""
def placing_possible(i,j):
    #print("I atual: {}".format(i))
    #print("J atual: {}".format(j))
    temp_list = []
    for u in range (i, i-panel_pix_y, -1):  #o menos é para detectar como bottom left
        for v in range (j, j+panel_pix_x, 1):
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
    for u in range (i, i-panel_pix_y, -1):
        for v in range (j, j+panel_pix_x, 1):
            placas_locadas[u][v] = placas_counter
    #for a in range (i-1-(panel_pix_x//2), i+1+(panel_pix_x//2), 1):
        #for b in range (i-1-(panel_pix_y//2), i+1+(panel_pix_y//2), 1):
            #print(placas_locadas[a][b])



def place_panels():
    global placas_counter, axis_lock, panel_pix_x, panel_pix_y
    x_axis = 0
    y_axis = 0
    for i in range(((panel_pix_y)+1), len(placas_locadas) - ((panel_pix_y)+1),1):
        print("Etapa {} de {}".format(i,len(placas_locadas)))
        for j in range(((panel_pix_x)+1),len(placas_locadas[0]) - ((panel_pix_x)+1),1):
            #print("Estamos no ponto {} {}".format(i,j))
            place_poss = placing_possible(i,j)
            if place_poss == True and axis_lock == False:
                placas_counter += 1
                execute_placing(i,j)
                lista_placas.append(Placa(placas_counter, area_de_interesse[i][j]))
                print("---------------------------")
                print("Placa locada: eixo {} {}".format(i,j))
                print("---------------------------")
            elif place_poss == True and axis_lock == True:
                if placas_counter == 0:
                    placas_counter += 1
                    execute_placing(i,j)
                    lista_placas.append(Placa(placas_counter, area_de_interesse[i][j]))
                    x_axis = j
                    y_axis = i
                    print("---------------------------")
                    print("Placa locada: eixo {} {}".format(i,j))
                    print("---------------------------")
                else:
                    if i == y_axis or j == x_axis:
                        placas_counter += 1
                        execute_placing(i,j)
                        lista_placas.append(Placa(placas_counter, area_de_interesse[i][j]))
                        #x_axis = j   #(pensar nessa possibilidade)
                        #y_axis = i   #(pensar nessa possibilidade)
                        print("---------------------------")
                        print("Placa locada: eixo {} {}".format(i,j))
                        print("---------------------------")
                    elif abs(i-y_axis) => panel_pix_y and abs(j-x_axis) => panel_pix_x:
                        placas_counter += 1
                        execute_placing(i,j)
                        lista_placas.append(Placa(placas_counter, area_de_interesse[i][j]))
                        #x_axis = j   #(pensar nessa possibilidade)
                        #y_axis = i   #(pensar nessa possibilidade)
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


placa_dim1 = 1.65
placa_dim2 = 1
orient = "Hor"
axis_lock = False

placa_dimx = None
placa_dimy = None

panel_pix_x = 11  #trocar depois nas funções
panel_pix_y = 21



"""Inicialização"""



file_area = open('area', 'rb')
area_de_interesse = pickle.load(file_area)

pix_dim=pixel_size()
incl = find_slope(area_de_interesse)


placa_projection()
print(placa_dimx, placa_dimy)
dimention_to_pixel()

print("Inclinação: {}".format(incl))

file_heatmap = open('heatmap', 'rb')
heatmap = pickle.load(file_heatmap)


placas_locadas = np.full_like(area_de_interesse, None)
lista_placas = []
placas_counter = 0

where_looking = np.full_like(area_de_interesse, None)



print(area_de_interesse.shape)
print(heatmap.shape)
print(placas_locadas.shape)

place_panels()
placas_img()

print(placas_locadas)
area_de_interesse_img()
where_looking_img()
overlay_images('output/Placas.png', 'output/Heatmap.png','output/placas_overlay.png')
