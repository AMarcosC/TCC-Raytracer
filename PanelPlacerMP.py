import numpy as np
import math
from BasicFunctions import *
from colour import Color
from PIL import Image
import multiprocessing
from multiprocessing import Pool
from tqdm import tqdm

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
    def __init__(self, id, coord, edges, score):
        self.id = id
        self.color = random_color()
        self.coord = coord
        self.edges = edges
        self.closest_shadow = None
        self.score = score


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
                elif slope(ar[i-1][j-1], ar[i+1][j+1]) > temp:  #corrigir depois, criar uma margem de erro para inclinação
                    temp = slope(ar[i-1][j-1], ar[i+1][j+1])
                    or_temp = 'other'
                elif slope(ar[i+1][j-1], ar[i-1][j+1]) > temp:
                    temp = slope(ar[i+1][j-1], ar[i-1][j+1])
                    or_temp = 'other'
                else:     #caso em que a inclinação é zero
                    temp = 0
                    or_temp = 'x'
                return (temp, or_temp)

def placa_projection(incl):
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
def alternate_orientation():
    global panel_pix_x, panel_pix_y
    temp_pix_x = panel_pix_x
    temp_pix_y = panel_pix_y
    panel_pix_x = temp_pix_y
    panel_pix_y = temp_pix_x

def routing_sequence(routing, orient_alternation):
    if routing == "top-left" and orient_alternation == False:
        begin_i = (panel_pix_y)+1
        end_i = len(heatmap) - ((panel_pix_y)+1)
        step_i = 1
        begin_j = (panel_pix_x)+1
        end_j = len(heatmap[0]) - ((panel_pix_x)+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "top-left" and orient_alternation == True:
        begin_i = (maior(panel_pix_y,panel_pix_x)+1)
        end_i = len(heatmap) - ((maior(panel_pix_y,panel_pix_x))+1)
        step_i = 1
        begin_j = ((maior(panel_pix_y,panel_pix_x))+1)
        end_j = len(heatmap[0]) - ((maior(panel_pix_y,panel_pix_x))+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "bottom-left" and orient_alternation == False:
        begin_i = len(heatmap) - ((panel_pix_y)+1)
        end_i = (panel_pix_y)+1
        step_i = -1
        begin_j = (panel_pix_x)+1
        end_j = len(heatmap[0]) - ((panel_pix_x)+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "bottom-left" and orient_alternation == True:
        begin_i = len(heatmap) - ((maior(panel_pix_y,panel_pix_x))+1)
        end_i = (maior(panel_pix_y,panel_pix_x)+1)
        step_i = -1
        begin_j = ((maior(panel_pix_y,panel_pix_x))+1)
        end_j = len(heatmap[0]) - ((maior(panel_pix_y,panel_pix_x))+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "top-right" and orient_alternation == False:
        begin_i = (panel_pix_y)+1
        end_i = len(heatmap) - ((panel_pix_y)+1)
        step_i = 1
        begin_j = len(heatmap[0]) - ((panel_pix_x)+1)
        end_j = (panel_pix_x+1)
        step_j = -1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "top-right" and orient_alternation == True:
        begin_i = (maior(panel_pix_y,panel_pix_x)+1)
        end_i = len(heatmap) - ((maior(panel_pix_y,panel_pix_x))+1)
        step_i = 1
        begin_j = len(heatmap[0]) - ((maior(panel_pix_y,panel_pix_x))+1)
        end_j = (maior(panel_pix_y,panel_pix_x)+1)
        step_j = -1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "bottom-right" and orient_alternation == False:
        begin_i = len(heatmap) - ((panel_pix_y)+1)
        end_i = (panel_pix_y)+1
        step_i = -1
        begin_j = len(heatmap[0]) - ((panel_pix_x)+1)
        end_j = (panel_pix_x+1)
        step_j = -1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "bottom-right" and orient_alternation == True:
        begin_i = len(heatmap) - ((maior(panel_pix_y,panel_pix_x))+1)
        end_i = (maior(panel_pix_y,panel_pix_x)+1)
        step_i = -1
        begin_j = len(heatmap[0]) - ((maior(panel_pix_y,panel_pix_x))+1)
        end_j = (maior(panel_pix_y,panel_pix_x)+1)
        step_j = -1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "left-top" and orient_alternation == False:
        begin_i = (panel_pix_y)+1
        end_i = len(heatmap) - ((panel_pix_y)+1)
        step_i = 1
        begin_j = (panel_pix_x)+1
        end_j = len(heatmap[0]) - ((panel_pix_x)+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "left-top" and orient_alternation == True:
        begin_i = (maior(panel_pix_y,panel_pix_x)+1)
        end_i = len(heatmap) - ((maior(panel_pix_y,panel_pix_x))+1)
        step_i = 1
        begin_j = ((maior(panel_pix_y,panel_pix_x))+1)
        end_j = len(heatmap[0]) - ((maior(panel_pix_y,panel_pix_x))+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "left-bottom" and orient_alternation == False:
        begin_i = len(heatmap) - ((panel_pix_y)+1)
        end_i = (panel_pix_y)+1
        step_i = -1
        begin_j = (panel_pix_x)+1
        end_j = len(heatmap[0]) - ((panel_pix_x)+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "left-bottom" and orient_alternation == True:
        begin_i = len(heatmap) - ((maior(panel_pix_y,panel_pix_x))+1)
        end_i = (maior(panel_pix_y,panel_pix_x)+1)
        step_i = -1
        begin_j = ((maior(panel_pix_y,panel_pix_x))+1)
        end_j = len(heatmap[0]) - ((maior(panel_pix_y,panel_pix_x))+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
        #continuar outros casos


def placing_possible(i,j,placas_locadas):  #jeito meio burro, dá pra simplificar como a de baixo
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

def placing_possible_in_shadow(i,j, placas_locadas):
    temp_list = []
    for u in range (i, i-panel_pix_y, -1):  #o menos é para detectar como bottom left
        for v in range (j, j+panel_pix_x, 1):
            if (placas_locadas[u][v] == None and
            #heatmap[u][v] == 0 #and
            area_de_interesse[u][v] != None
            ):
                temp_list.append(True)
            else:
                temp_list.append(False)
    for value in temp_list:
        if value == False:
            return False
    return True


def execute_placing(i,j,score, placas_locadas, lista_placas, placas_counter):
    placas_counter += 1
    for u in range (i, i-panel_pix_y, -1):
        for v in range (j, j+panel_pix_x, 1):
            placas_locadas[u][v] = placas_counter
    lista_placas.append(Placa(placas_counter, area_de_interesse[i][j], panel_edge_pixels(i,j), score))
    print("---------------------------")
    print("Placa locada: eixo {} {}".format(i,j))
    print("---------------------------")


def panel_edge_pixels(i,j):
    t_l = [j, i-panel_pix_y+1]
    t_r = [j+panel_pix_x-1, i-panel_pix_y+1]
    b_l = [j, i]
    b_r = [j+panel_pix_x-1, i]
    return [t_l, t_r, b_l, b_r]


def place_panels(lista_placas, placas_counter, placas_locadas, routing, orient_alternation, pbar):
    index = routing_sequence(routing, orient_alternation)
    for i in range(index[0][0], index[0][1], index[0][2]):
        #print("Etapa {} de {}".format(i,len(placas_locadas)))
        pbar.update(1)
        for j in range(index[1][0], index[1][1], index[1][2]):
            #print("Estamos no ponto {} {}".format(i,j))
            if placing_possible(i,j, placas_locadas) == True:
                execute_placing(i,j,1.0, placas_locadas, lista_placas, placas_counter)
            else:   #apenas por motivos de debug
                continue


def place_panels_updown_route(lista_placas, placas_counter, routing, orient_alternation):
    index = routing_sequence(routing, orient_alternation)
    for j in range(index[1][0], index[1][1], index[1][2]):
        #print("Etapa {} de {}".format(i,len(placas_locadas)))
        pbar.update(1)
        for i in range(index[0][0], index[0][1], index[0][2]):
            #print("Estamos no ponto {} {}".format(i,j))
            if placing_possible(i,j) == True:
                execute_placing(i,j,1.0)
            else:   #apenas por motivos de debug
                continue


def place_panels_alternate_orient(routing, orient_alternation):
    global placas_counter, lista_placas
    index = routing_sequence(routing, orient_alternation)
    x_axis = 0
    y_axis = 0
    for i in range(index[0][0], index[0][1], index[0][2]):
        #print("Etapa {} de {}".format(i,len(placas_locadas)))
        pbar.update(1)
        for j in range(index[1][0], index[1][1], index[1][2]):
            #print("Estamos no ponto {} {}".format(i,j))
            if placing_possible(i,j) == True:
                execute_placing(i,j,1.0)
            else:
                alternate_orientation()
                if placing_possible(i,j) == True:
                    execute_placing(i,j,1.0)
                alternate_orientation()
                continue


def place_panels_aligned(routing, orient_alternation):  #será substituída
    global placas_counter, axis_lock, panel_pix_x, panel_pix_y, lista_placas
    index = routing_sequence(routing, orient_alternation)
    x_axis = 0
    y_axis = 0
    for i in range(index[0][0], index[0][1], index[0][2]):
        print("Etapa {} de {}".format(i,len(placas_locadas)))
        for j in range(index[1][0], index[1][1], index[1][2]):
            #print("Estamos no ponto {} {}".format(i,j))
            place_poss = placing_possible(i,j)
            if place_poss == True and axis_lock == False:
                execute_placing(i,j,1.0)
            elif place_poss == True and axis_lock == True:
                if placas_counter == 0:
                    execute_placing(i,j,1.0)
                    x_axis = j
                    y_axis = i
                else:
                    if i == y_axis or j == x_axis:
                        execute_placing(i,j,1.0)
                        #x_axis = j   #(pensar nessa possibilidade)
                        #y_axis = i   #(pensar nessa possibilidade)
                    elif abs(i-y_axis) >= panel_pix_y and abs(j-x_axis) >= panel_pix_x:
                        execute_placing(i,j,1.0)
                        #x_axis = j   #(pensar nessa possibilidade)
                        #y_axis = i   #(pensar nessa possibilidade)
            else:   #apenas por motivos de debug
                continue


def place_panels_in_grid(case, placas_locadas):
    global placas_counter, panel_pix_x, panel_pix_y, lista_placas, needed_placas
    grid = return_all_grid_points(case)
    grid_filter = []
    grid_optimum = []
    for p in grid:
        if placing_possible_in_shadow(p[1], p[0], placas_locadas) == True:
            p[2] = panel_score(p[1], p[0])
            if p[2] > 0.999:
                grid_optimum.append(p)
            else:
                grid_filter.append(p)
    print(grid_filter)
    for i in range(0, len(grid_optimum), 1):
        if placas_counter < needed_placas:
            execute_placing(grid_optimum[i][1], grid_optimum[i][0], grid_optimum[i][2])
    while placas_counter < needed_placas:
        p_sha = highest_score_position(grid_filter)
        execute_placing(p_sha[1], p_sha[0], p_sha[2])
        del grid_filter[p_sha[3]]




def all_grid_points(i,j,case):
    print(case)
    global panel_pix_x, panel_pix_y, heatmap
    temp_x_less = j
    temp_x_plus = j + panel_pix_x
    temp_y_less = i
    temp_y_plus = i + panel_pix_y
    x_list = []
    y_list = []
    coord = []
    while temp_x_less >= 0:
        x_list.append(temp_x_less)
        temp_x_less += -panel_pix_x
    while temp_x_plus <= len(heatmap[0])-panel_pix_x-1:
        x_list.append(temp_x_plus)
        temp_x_plus += panel_pix_x
    while temp_y_less >= panel_pix_x:  #verificar
        y_list.append(temp_y_less)
        temp_y_less += -panel_pix_y
    while temp_y_plus <= len(heatmap)-1:
        y_list.append(temp_y_plus)
        temp_y_plus += panel_pix_y
    if case == 'top-left':
        x_list.sort()
        y_list.sort()
        for y in y_list:
            for x in x_list:
                coord.append([x, y, 0])
    elif case == 'top-right':
        x_list.sort(reverse=True)
        y_list.sort()
        for y in y_list:
            for x in x_list:
                coord.append([x, y, 0])
    elif case == "bottom-right":
        x_list.sort(reverse=True)
        y_list.sort(reverse=True)
        for y in y_list:
            for x in x_list:
                coord.append([x, y, 0])
    elif case == "bottom-left":
        x_list.sort()
        y_list.sort(reverse=True)
        for y in y_list:
            for x in x_list:
                coord.append([x, y, 0])
    return coord

def return_all_grid_points(case, routing, orient_alternation):
    index = routing_sequence(routing, orient_alternation)
    for i in range(index[0][0], index[0][1], index[0][2]):
        print("Etapa {} de {}".format(i,len(placas_locadas)))
        for j in range(index[1][0], index[1][1], index[1][2]):
            if placing_possible(i,j) == True:
                return all_grid_points(i,j,case)


def return_placa_color(ident, lista_placas):
    for placa in lista_placas:
        if placa.id == ident:
            return placa.color

def placas_img(c_index, placas_locadas, lista_placas):
    soma = placas_locadas
    img = []
    for i in soma:
        line = []
        for j in i:
            if j != None and j >= 0:
                line.append(return_placa_color(j, lista_placas))
            else:
                line.append([255,255,255,0])
        img.append(line)
    img1 = Image.fromarray(np.uint8(img)).convert('RGBA')  #Transformando a matriz em uma imagem .png
    img1.save('output/{}-Placas_{}_orient-{}_{}placas.png'.format(c_index, routing, orient, placas_counter))
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


def print_placas():  #para debug
    global lista_placas
    print("------ Listagem das Placas ------")
    for placa in lista_placas:
        print("---- Placa {} ----".format(placa.id))
        print("Coordenada: x:{} y:{} z:{}".format(placa.coord.x, placa.coord.y, placa.coord.z))
        print("Bordas em px: {}".format(placa.edges))
        print("Score: {}".format(placa.score))
    print("---------------------------------")

def get_closest_shadows(value):   #problemática, não será mais o foco
    global lista_placas, pix_x, pix_y
    for placa in lista_placas:
        edges = placa.edges
        upper = 0
        lower = 0
        left = 0
        right = 0
        #investigando da borda superior para cima
        print("Investigando a placa {}".format(placa.id))
        pix_upper = 0
        for i in range (edges[0][0], edges[1][0]+1, 1):
            temp_index = edges[0][1] - 1
            while (
            area_de_interesse[i][temp_index] != None and
            heatmap[i][temp_index] <= value and
            placas_locadas[i][temp_index] == None
            ):
                temp_index += -1
            if abs(edges[0][1] - temp_index) > pix_upper:
                pix_upper = abs(edges[0][1] - temp_index)
        upper = pix_upper*pix_y
        #investigando da borda inferior para baixo
        pix_lower = 0
        for j in range (edges[2][0], edges[3][0]+1, 1):
            temp_index = edges[2][1] + 1
            while (
            area_de_interesse[j][temp_index] != None and
            heatmap[j][temp_index] <= value and
            placas_locadas[j][temp_index] == None
            ):
                temp_index += 1
            if abs(edges[2][1] - temp_index) > pix_lower:
                pix_lower = abs(edges[2][1] - temp_index)
        lower = pix_lower*pix_y
        #investigando da borda esquerda para a esquerda
        pix_left = 0
        for u in range (edges[0][1], edges[2][1]+1, 1):
            temp_index = edges[0][0] - 1
            while (
            area_de_interesse[temp_index][u] != None and
            heatmap[temp_index][u] <= value and
            placas_locadas[temp_index][u] == None
            ):
                temp_index += -1
            if abs(edges[0][0] - temp_index) > pix_left:
                pix_left = abs(edges[0][0] - temp_index)
        left = pix_left*pix_y
        #investigando da borda direita para a direita
        pix_right = 0
        for v in range (edges[1][1], edges[3][1]+1, 1):
            temp_index = edges[1][0] + 1
            while (
            area_de_interesse[temp_index][v] != None and
            heatmap[temp_index][v] <= value and
            placas_locadas[temp_index][v] == None
            ):
                temp_index += 1
            if abs(edges[1][0] - temp_index) > pix_right:
                pix_right = abs(edges[1][0] - temp_index)
        right = pix_right*pix_y
        placa.closest_shadow = [upper, lower, left, right]


def panel_score(i, j):
    global highest_sha_value, panel_pix_x, panel_pix_y
    cumulative_value = 0
    for u in range (i, i-panel_pix_y, -1):  #o menos é para detectar como bottom left
        for v in range (j, j+panel_pix_x, 1):
            cumulative_value += (highest_sha_value - heatmap[u][v])
    return (cumulative_value / (highest_sha_value*panel_pix_x*panel_pix_y))

def best_placing(placas_counter, lista_placas, placas_locadas, routing, orient_alternation, pbar):
    index = routing_sequence(routing, orient_alternation)
    best_score = 0
    cbp = [0, 0]  #current best place
    print("Procurando melhor encaixe...")
    for i in range(index[0][0], index[0][1], index[0][2]):
        pbar.update(1)
        for j in range(index[1][0], index[1][1], index[1][2]):
            #print("Estamos no ponto {} {}".format(i,j))
            if placing_possible_in_shadow(i,j, placas_locadas) == True:
                temp_score = panel_score(i,j)
                if temp_score > best_score:
                    best_score = temp_score
                    cbp = [i, j]
                elif temp_score == best_score:
                    print("Empate!")
    execute_placing(cbp[0],cbp[1], best_score, placas_locadas, lista_placas, placas_counter)


def highest_score_position(grid_list):
    temp_score = -1
    temp_x = 0
    temp_y = 0
    temp_index = 0
    for i in range(0, len(grid_list), 1):
        if grid_list[i][2] > temp_score:
            temp_score = grid_list[i][2]
            temp_x = grid_list[i][0]
            temp_y = grid_list[i][1]
            temp_index = i
    return [temp_x, temp_y, temp_score, temp_index]

def case_resolution_normal(case):
    lista_placas = []
    placas_counter = 0
    case_index = cases.index(case)
    print("-------------------------")
    print("----Iniciando caso {}----".format(cases.index(case)))
    print("-------------------------")
    pbar = tqdm(total=len(heatmap))
    orient = case[0]
    routing = case[1]
    axis_lock = case[2]
    orient_alternation = case[3]
    pix_dim=pixel_size()
    incl = find_slope(area_de_interesse)
    placa_projection(incl)
    print(placa_dimx, placa_dimy)
    dimention_to_pixel()
    print("Inclinação: {}".format(incl))
    placas_locadas = np.full_like(area_de_interesse, None)
    if axis_lock == True and orient_alternation == False:
        place_panels_aligned()
    elif axis_lock == False and orient_alternation == True:
        place_panels_alternate_orient()
    elif axis_lock == True and orient_alternation == True:
        print("Não há função para este caso!")
        place_panels(lista_placas, placas_counter, placas_locadas, routing, orient_alternation, pbar)
    else:
        place_panels(lista_placas, placas_counter, placas_locadas, routing, orient_alternation, pbar)
    #while placas_counter < needed_placas:
    #    pbar_best = tqdm(total=len(heatmap))
    #    best_placing(placas_counter, lista_placas, placas_locadas, routing, orient_alternation, pbar_best)
    placas_img(case_index, placas_locadas, lista_placas)
    #overlay_images('output/{}-Placas_{}_orient-{}_{}placas.png'.format(case_index, routing, orient, placas_counter), 'output/Heatmap.png','output/{}-placas_overlay.png'.format(cases.index(case)))


"""Variáveis Globais"""
core_count=multiprocessing.cpu_count()
print("Número de núcleos da CPU: {}".format(core_count))

pix_x = None
pix_y = None
pix_area = None

needed_placas = 21
placa_dim1 = 1.65
placa_dim2 = 1
orient = "Hor"
routing = "bottom-right"
axis_lock = False
orient_alternation = False

placa_dimx = None
placa_dimy = None

panel_pix_x = 11  #trocar depois nas funções
panel_pix_y = 21


"""Inicialização"""
#Ordem: orient, routing, axis_lock, orient_alternation

cases = [
['Hor', 'top-left', False, False],
['Hor', 'top-right', False, False],
['Hor', 'bottom-left', False, False],
['Hor', 'bottom-right', False, False],
#['Vert', 'bottom-right', True, False],
#['Vert', 'bottom-right', False, True],
]

lista_placas = []
placas_counter = 0

file_area = open('area', 'rb')
area_de_interesse = pickle.load(file_area)

file_heatmap = open('heatmap', 'rb')
heatmap = pickle.load(file_heatmap)
highest_sha_value = highest_value_in_array(heatmap)
print("O maior valor de sombreamento é {}".format(highest_sha_value))

"""
#Proposta 01

#execução de todos os casos
for case in cases:
    case_index = cases.index(case)
    print("-------------------------")
    print("----Iniciando caso {}----".format(cases.index(case)))
    print("-------------------------")
    orient = case[0]
    routing = case[1]
    axis_lock = case[2]
    orient_alternation = case[3]
    pix_dim=pixel_size()
    incl = find_slope(area_de_interesse)
    placa_projection()
    print(placa_dimx, placa_dimy)
    dimention_to_pixel()
    print("Inclinação: {}".format(incl))
    placas_locadas = np.full_like(area_de_interesse, None)
    if axis_lock == True and orient_alternation == False:
        place_panels_aligned()
    elif axis_lock == False and orient_alternation == True:
        place_panels_alternate_orient()
    elif axis_lock == True and orient_alternation == True:
        print("Não há função para este caso!")
        place_panels()
    else:
        place_panels()
    while placas_counter < needed_placas:
        best_placing()
    placas_img(case_index)
    overlay_images('output/{}-Placas_{}_orient-{}_{}placas.png'.format(case_index, routing, orient, placas_counter), 'output/Heatmap.png','output/{}-placas_overlay.png'.format(cases.index(case)))
"""


"""
for case in cases:
    case_index = cases.index(case)
    print("-------------------------")
    print("----Iniciando caso {}----".format(cases.index(case)))
    print("-------------------------")
    orient = case[0]
    routing = case[1]
    axis_lock = case[2]
    orient_alternation = case[3]
    pix_dim=pixel_size()
    incl = find_slope(area_de_interesse)
    placa_projection()
    print(placa_dimx, placa_dimy)
    dimention_to_pixel()
    print("Inclinação: {}".format(incl))
    placas_locadas = np.full_like(area_de_interesse, None)
    place_panels_in_grid(routing)
    placas_img(case_index)
    overlay_images(r'output/{}-Placas_{}_orient-{}_{}placas.png'.format(case_index, routing, orient, placas_counter), 'output/Heatmap.png','output/{}-placas_overlay.png'.format(cases.index(case)))
"""

pool = Pool(processes=core_count-1)  #aumentar ou diminuir depois
results = pool.imap_unordered(case_resolution_normal, cases, chunksize=1)
for result in results:
    print("Terminado!")
pool.close() # No more work
pool.join() # Wait for completion

print_placas()

python_array_to_pickle(lista_placas, 'lista_placas')
