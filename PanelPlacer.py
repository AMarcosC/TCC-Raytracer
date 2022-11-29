import numpy as np
import math
from BasicFunctions import *
from colour import Color
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

"""
Observações:

É desnecessário utilizar a matriz da área de interesse na locação, já que o mapa de calor só existe na área de interesse mesmo.
Porém ela pode ser utilizada para verificar a inclinação do telhado.

Possíveis aprimoramentos no código:
- O mapeamento horizontal e vertical podem ser unidos em uma única função, bastando um if statement

"""

"""Classes"""

class Placa:  #classse que define as propriedades de um objeto genérico qualquer
    def __init__(self, id, coord, edges, score):
        self.id = id
        self.color = random_bright_color()
        self.coord = coord
        self.edges = edges
        self.closest_shadow = None
        self.score = score


"""Funções"""

def pixel_size():  #define o tamanho de um pixel no mundo real, no eixo x e no eixo y
    global pix_x, pix_y, pix_area, area_de_interesse, pix_dens
    if pix_dens <= 0:
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
                    x_dens = round(1/round(pix_x,4))
                    y_dens = round(1/round(pix_y,4))
                    if x_dens != y_dens:
                        print("Erro: Densidades verticais e horizontais não são iguais. Inserir densidade manualmente")
                    else:
                        pix_dens = x_dens
                    print("Altura do pixel: {}".format(pix_y))
                    print("Largura do pixel: {}".format(pix_x))
                    print("Área do pixel: {}".format(pix_area))
                    return(pix_x,pix_y)
    else:
        pix_x = 1/pix_dens
        pix_y = 1/pix_dens
        pix_area = pix_x * pix_y
        print("Altura do pixel: {}".format(pix_y))
        print("Largura do pixel: {}".format(pix_x))
        print("Área do pixel: {}".format(pix_area))
        return(pix_x,pix_y)

def not_surrounded_by(array,i,j,value):  #verifica se um certo índice da matriz não é rodeado por um certo valor
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

def slope(p0, p1):  #calcula a inclinação entre dois pontos
    dx = p1.x - p0.x
    dy = p1.y - p0.y
    dz = p1.z - p0.z
    dl = math.sqrt((dx**2) + (dy**2))
    return (abs(dz/dl))  #radianos

def find_slope(ar):  #encontra a inclinação do telhado  #vai servir para o exemplo mas é muito arcaico, é melhor que esse valor venha do modelo
    global incl_pref, incl_value, incl_orient
    if incl_pref == "Telhado":
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
                    elif slope(ar[i-1][j-1], ar[i+1][j+1]) > temp:  #criar uma margem de erro para inclinação
                        temp = slope(ar[i-1][j-1], ar[i+1][j+1])
                        or_temp = 'other'
                    elif slope(ar[i+1][j-1], ar[i-1][j+1]) > temp:
                        temp = slope(ar[i+1][j-1], ar[i-1][j+1])
                        or_temp = 'other'
                    else:     #caso em que a inclinação é zero
                        temp = 0
                        or_temp = 'x'
                    return (temp, or_temp)
    elif incl_pref == "Placa":
        temp = math.radians(incl_value)
        or_temp = incl_orient
        return (temp, or_temp)

def placa_projection():  #determina qual direção da placa será inclinada e faz a sua projeção no plano
    global placa_dim1, placa_dim2, placa_dimx, placa_dimy
    alpha = math.cos(math.atan(incl[0]))
    print(alpha)
    if orient == 'Vert' and (incl[1] == 'x' or incl[1] == '-x'):
        placa_dimx = menor(placa_dim1, placa_dim2) * alpha
        placa_dimy = maior(placa_dim1, placa_dim2)
    elif orient == 'Vert' and (incl[1] == 'y' or incl[1] == '-y'):
        placa_dimx = menor(placa_dim1, placa_dim2)
        placa_dimy = maior(placa_dim1, placa_dim2) * alpha
    elif orient =='Hor' and (incl[1] == 'x' or incl[1] == '-x'):
        placa_dimx = maior(placa_dim1, placa_dim2) * alpha
        placa_dimy = menor(placa_dim1, placa_dim2)
    elif orient =='Hor' and (incl[1] == 'y' or incl[1] == '-y'):
        placa_dimx = maior(placa_dim1, placa_dim2)
        placa_dimy = menor(placa_dim1, placa_dim2) * alpha


def z_diff(ext, ori, val):  #determina a diferença de altura na inclinação da placa  #extremidades, sentido da incl da placa, angulo
    if ori == 'x':
        z_keep = ext[0].z
        h_0 = ext[0].x
        h_1 = ext[1].x
        dist = abs(h_1 - h_0)
        z_diff_v = dist*math.tan(val)
        z_new = z_keep + z_diff_v
        ext[1].z = z_new
        ext[3].z = z_new
        return ext
    elif ori == '-x':
        z_keep = ext[1].z
        h_0 = ext[0].x
        h_1 = ext[1].x
        dist = abs(h_1 - h_0)
        z_diff_v = dist*math.tan(val)
        z_new = z_keep + z_diff_v
        ext[0].z = z_new
        ext[2].z = z_new
        return ext
    elif ori == 'y':
        z_keep = ext[2].z
        h_0 = ext[0].y
        h_1 = ext[2].y
        dist = abs(h_1 - h_0)
        z_diff_v = dist*math.tan(val)
        z_new = z_keep + z_diff_v
        ext[0].z = z_new
        ext[1].z = z_new
        return ext
    elif ori == '-y':
        z_keep = ext[0].z
        h_0 = ext[0].y
        h_1 = ext[2].y
        dist = abs(h_1 - h_0)
        z_diff_v = dist*math.tan(val)
        z_new = z_keep + z_diff_v
        ext[2].z = z_new
        ext[3].z = z_new
        return ext


def dimention_to_pixel(): #converte uma dimensão do mundo real em valores inteiros de pixel
    global panel_pix_x, panel_pix_y
    panel_pix_x = math.ceil(placa_dimx/round(pix_x,3))
    panel_pix_y = math.ceil(placa_dimy/round(pix_y,3))
    print("Placa terá {} px em X e {} px em Y".format(panel_pix_x,panel_pix_y))
    print("O tamanho real será de {} m em X e {} m em Y".format(panel_pix_x*round(pix_x,3),panel_pix_y*round(pix_y,3)))


def alternate_orientation():  #alterna a orientação da placa
    global panel_pix_x, panel_pix_y
    temp_pix_x = panel_pix_x
    temp_pix_y = panel_pix_y
    panel_pix_x = temp_pix_y
    panel_pix_y = temp_pix_x

def routing_sequence():  #define os índices do laço que vai escanear a cena
    global routing, orient_alternation
    if routing == "top-left" and orient_alternation == False:
        begin_i = (panel_pix_y)+1
        end_i = len(placas_locadas) - ((panel_pix_y)+1)
        step_i = 1
        begin_j = (panel_pix_x)+1
        end_j = len(placas_locadas[0]) - ((panel_pix_x)+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "top-left" and orient_alternation == True:
        begin_i = (maior(panel_pix_y,panel_pix_x)+1)
        end_i = len(placas_locadas) - ((maior(panel_pix_y,panel_pix_x))+1)
        step_i = 1
        begin_j = ((maior(panel_pix_y,panel_pix_x))+1)
        end_j = len(placas_locadas[0]) - ((maior(panel_pix_y,panel_pix_x))+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "bottom-left" and orient_alternation == False:
        begin_i = len(placas_locadas) - ((panel_pix_y)+1)
        end_i = (panel_pix_y)+1
        step_i = -1
        begin_j = (panel_pix_x)+1
        end_j = len(placas_locadas[0]) - ((panel_pix_x)+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "bottom-left" and orient_alternation == True:
        begin_i = len(placas_locadas) - ((maior(panel_pix_y,panel_pix_x))+1)
        end_i = (maior(panel_pix_y,panel_pix_x)+1)
        step_i = -1
        begin_j = ((maior(panel_pix_y,panel_pix_x))+1)
        end_j = len(placas_locadas[0]) - ((maior(panel_pix_y,panel_pix_x))+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "top-right" and orient_alternation == False:
        begin_i = (panel_pix_y)+1
        end_i = len(placas_locadas) - ((panel_pix_y)+1)
        step_i = 1
        begin_j = len(placas_locadas[0]) - ((panel_pix_x)+1)
        end_j = (panel_pix_x+1)
        step_j = -1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "top-right" and orient_alternation == True:
        begin_i = (maior(panel_pix_y,panel_pix_x)+1)
        end_i = len(placas_locadas) - ((maior(panel_pix_y,panel_pix_x))+1)
        step_i = 1
        begin_j = len(placas_locadas[0]) - ((maior(panel_pix_y,panel_pix_x))+1)
        end_j = (maior(panel_pix_y,panel_pix_x)+1)
        step_j = -1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "bottom-right" and orient_alternation == False:
        begin_i = len(placas_locadas) - ((panel_pix_y)+1)
        end_i = (panel_pix_y)+1
        step_i = -1
        begin_j = len(placas_locadas[0]) - ((panel_pix_x)+1)
        end_j = (panel_pix_x+1)
        step_j = -1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "bottom-right" and orient_alternation == True:
        begin_i = len(placas_locadas) - ((maior(panel_pix_y,panel_pix_x))+1)
        end_i = (maior(panel_pix_y,panel_pix_x)+1)
        step_i = -1
        begin_j = len(placas_locadas[0]) - ((maior(panel_pix_y,panel_pix_x))+1)
        end_j = (maior(panel_pix_y,panel_pix_x)+1)
        step_j = -1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "left-top" and orient_alternation == False:
        begin_i = (panel_pix_y)+1
        end_i = len(placas_locadas) - ((panel_pix_y)+1)
        step_i = 1
        begin_j = (panel_pix_x)+1
        end_j = len(placas_locadas[0]) - ((panel_pix_x)+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "left-top" and orient_alternation == True:
        begin_i = (maior(panel_pix_y,panel_pix_x)+1)
        end_i = len(placas_locadas) - ((maior(panel_pix_y,panel_pix_x))+1)
        step_i = 1
        begin_j = ((maior(panel_pix_y,panel_pix_x))+1)
        end_j = len(placas_locadas[0]) - ((maior(panel_pix_y,panel_pix_x))+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "left-bottom" and orient_alternation == False:
        begin_i = len(placas_locadas) - ((panel_pix_y)+1)
        end_i = (panel_pix_y)+1
        step_i = -1
        begin_j = (panel_pix_x)+1
        end_j = len(placas_locadas[0]) - ((panel_pix_x)+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
    elif routing == "left-bottom" and orient_alternation == True:
        begin_i = len(placas_locadas) - ((maior(panel_pix_y,panel_pix_x))+1)
        end_i = (maior(panel_pix_y,panel_pix_x)+1)
        step_i = -1
        begin_j = ((maior(panel_pix_y,panel_pix_x))+1)
        end_j = len(placas_locadas[0]) - ((maior(panel_pix_y,panel_pix_x))+1)
        step_j = 1
        return [[begin_i, end_i, step_i],[begin_j,end_j,step_j]]
        #continuar outros casos se a nomenclatura vertical-horizontal for aplicada


def placing_possible(i,j):  #verifica se é possivel colocar a placa, considerando apenas áreas sem sombreamento
    temp_list = []
    for u in range (i, i-panel_pix_y, -1):  #o menos é para detectar como bottom left
        for v in range (j, j+panel_pix_x, 1):
            if (placas_locadas[u][v] == None and heatmap[u][v] == 0):
                temp_list.append(True)
            else:
                temp_list.append(False)
    for value in temp_list:
        if value == False:
            return False
    return True

def placing_possible_in_shadow(i,j):  #verifica se é possivel colocar a placa, mesmo em áreas sombreadas
    temp_list = []
    for u in range (i, i-panel_pix_y, -1):  #o menos é para detectar como bottom left
        for v in range (j, j+panel_pix_x, 1):
            if (placas_locadas[u][v] == None and area_de_interesse[u][v] != None):
                temp_list.append(True)
            else:
                temp_list.append(False)
    for value in temp_list:
        if value == False:
            return False
    return True


def execute_placing(i,j,score):  #executa a colocação da placa na posição
    global lista_placas, placas_counter
    placas_counter += 1
    for u in range (i, i-panel_pix_y, -1):
        for v in range (j, j+panel_pix_x, 1):
            placas_locadas[u][v] = placas_counter
    lista_placas.append(Placa(placas_counter, panel_edge_coord(i,j), panel_edge_pixels(i,j), score))
    #print("---------------------------")
    #print("Placa locada: eixo {} {}".format(i,j))
    #print("---------------------------")


def panel_edge_pixels(i,j):  #determina as bordas da placa em pixels
    t_l = [j, i-panel_pix_y+1]
    t_r = [j+panel_pix_x-1, i-panel_pix_y+1]
    b_l = [j, i]
    b_r = [j+panel_pix_x-1, i]
    return [t_l, t_r, b_l, b_r]

def panel_edge_coord(i,j):  #determina as bordas da placa nas suas coordenadas reais (considerando as dimensões da precisão dos pixels, e não as do manual da placa)
    global incl_pref, incl
    ed = panel_edge_pixels(i,j)
    t_l_coord = area_de_interesse[ed[0][1]][ed[0][0]]
    t_r_coord = area_de_interesse[ed[1][1]][ed[1][0]]
    b_l_coord = area_de_interesse[ed[2][1]][ed[2][0]]
    b_r_coord = area_de_interesse[ed[3][1]][ed[3][0]]
    coord_result = [t_l_coord, t_r_coord, b_l_coord, b_r_coord]
    if incl_pref == "Placa":
        return z_diff(coord_result, incl[1], incl[0])
    elif incl_pref == "Telhado":
        return coord_result

def place_panels():  #insere placas na imagem, na modalidade livre, mapeamento horizontal
    global placas_counter, lista_placas
    index = routing_sequence()
    for i in range(index[0][0], index[0][1], index[0][2]):
        print("Etapa {} de {}".format(i,len(placas_locadas)))
        for j in range(index[1][0], index[1][1], index[1][2]):
            #print("Estamos no ponto {} {}".format(i,j))
            if placing_possible(i,j) == True:
                execute_placing(i,j,1.0)
            else:   #apenas por motivos de debug
                continue


def place_panels_updown_route(): #insere placas na imagem, na modalidade livre, mapeamento vertical
    global placas_counter, lista_placas
    index = routing_sequence()
    for j in range(index[1][0], index[1][1], index[1][2]):  #a única diferença entre esta funcão e a anterior é que i e j estão trocados
        print("Etapa {} de {}".format(j,len(placas_locadas[0])))
        for i in range(index[0][0], index[0][1], index[0][2]):
            #print("Estamos no ponto {} {}".format(i,j))
            if placing_possible(i,j) == True:
                execute_placing(i,j,1.0)
            else:   #apenas por motivos de debug
                continue


def place_panels_alternate_orient():  #insere placas na imagem, modalidade alternando orientação, mapeamento horizontal
    global placas_counter, lista_placas
    index = routing_sequence()
    x_axis = 0
    y_axis = 0
    for i in range(index[0][0], index[0][1], index[0][2]):
        print("Etapa {} de {}".format(i,len(placas_locadas)))
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



def place_panels_in_grid(case):  #insere placas na imagem, modalidade alinahdo
    global placas_counter, panel_pix_x, panel_pix_y, lista_placas, needed_placas
    grid = return_all_grid_points(case)
    grid_filter = []
    grid_optimum = []
    for p in grid:
        if placing_possible_in_shadow(p[1], p[0]) == True:
            p[2] = panel_score(p[1], p[0])
            if p[2] > 0.999:
                grid_optimum.append(p)
            else:
                grid_filter.append(p)
    print(grid_filter)
    for i in range(0, len(grid_optimum), 1):
        if placas_counter < needed_placas:
            execute_placing(grid_optimum[i][1], grid_optimum[i][0], grid_optimum[i][2])
    while placas_counter < needed_placas and len(grid_filter) > 0:
        p_sha = highest_score_position(grid_filter)
        execute_placing(p_sha[1], p_sha[0], p_sha[2])
        del grid_filter[p_sha[3]]


def place_panels_in_grids_possible(case): #insere placas na imagem, modalidade alinahdo, verificando todos os resultados possíveis
    global placas_counter, panel_pix_x, panel_pix_y, lista_placas, needed_placas, placas_locadas
    grid_init_coord = combinations_in_grid()
    best_placas_locadas = np.full_like(area_de_interesse, None)
    best_placas_counter = 0
    best_lista_placas = []
    best_score = -1
    for g in grid_init_coord:
        print("Score atual: {}".format(best_score))
        placas_locadas = np.full_like(area_de_interesse, None)
        placas_counter = 0
        lista_placas = []
        grid = all_grid_points(g[0], g[1], case)
        grid_filter = []
        grid_optimum = []
        for p in grid:
            if placing_possible_in_shadow(p[1], p[0]) == True:
                p[2] = panel_score(p[1], p[0])
                if p[2] > 0.99999:
                    grid_optimum.append(p)
                else:
                    grid_filter.append(p)
        for i in range(0, len(grid_optimum), 1):
            if placas_counter < needed_placas:
                execute_placing(grid_optimum[i][1], grid_optimum[i][0], grid_optimum[i][2])
        while placas_counter < needed_placas and len(grid_filter) > 0:
            p_sha = highest_score_position(grid_filter)
            execute_placing(p_sha[1], p_sha[0], p_sha[2])
            del grid_filter[p_sha[3]]
        temp_score = overall_score(lista_placas)
        if temp_score >= best_score:
            best_placas_locadas = placas_locadas
            best_placas_counter = placas_counter
            best_lista_placas = lista_placas
            best_score = temp_score
    placas_locadas = best_placas_locadas
    placas_counter = best_placas_counter
    lista_placas = best_lista_placas
    print('Melhor score: {}'.format(best_score))




def all_grid_points(i,j,case):  #determina todos os pontos de um grid, a partir de um ponto inicial
    global panel_pix_x, panel_pix_y, heatmap, grid_order_routing, afastamento
    x_list = []
    y_list = []
    coord = []
    #este trecho determina os pontos iniciais da procura
    if afastamento == 0:
        temp_x_less = j
        temp_x_plus = j + panel_pix_x
        temp_y_less = i
        temp_y_plus = i + panel_pix_y
    elif afastamento != 0 and (incl_orient == '-y' or incl_orient == 'y'):
        temp_x_less = j
        temp_x_plus = j + panel_pix_x
        temp_y_less = i
        temp_y_plus = i + panel_pix_y + afastamento
    elif afastamento != 0 and (incl_orient == '-x' or incl_orient == 'x'):
        temp_x_less = j
        temp_x_plus = j + panel_pix_x + afastamento
        temp_y_less = i
        temp_y_plus = i + panel_pix_y
    #este trecho faz a procura de todos os outros pontos a partir do laço
    if afastamento == 0:
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
    elif afastamento > 0 and (incl_orient == '-y' or incl_orient == 'y'):
        while temp_x_less >= 0:
            x_list.append(temp_x_less)
            temp_x_less += -panel_pix_x
        while temp_x_plus <= len(heatmap[0])- panel_pix_x -1:
            x_list.append(temp_x_plus)
            temp_x_plus += panel_pix_x
        while temp_y_less >= panel_pix_x:  #verificar
            y_list.append(temp_y_less)
            temp_y_less += - panel_pix_y - afastamento
        while temp_y_plus <= len(heatmap)-1:
            y_list.append(temp_y_plus)
            temp_y_plus += panel_pix_y + afastamento
    elif afastamento > 0 and (incl_orient == '-x' or incl_orient == 'x'):
        while temp_x_less >= 0:
            x_list.append(temp_x_less)
            temp_x_less += -panel_pix_x - afastamento
        while temp_x_plus <= len(heatmap[0])-panel_pix_x-1:
            x_list.append(temp_x_plus)
            temp_x_plus += panel_pix_x + afastamento
        while temp_y_less >= panel_pix_x:  #verificar
            y_list.append(temp_y_less)
            temp_y_less += -panel_pix_y
        while temp_y_plus <= len(heatmap)-1:
            y_list.append(temp_y_plus)
            temp_y_plus += panel_pix_y + afastamento
    #este trecho ordena os pontos a partir das definições do usuário
    if case == 'top-left' and grid_order_routing=='LR':
        x_list.sort()
        y_list.sort()
        for y in y_list:
            for x in x_list:
                coord.append([x, y, 0])
    elif case == 'top-right' and grid_order_routing=='LR':
        x_list.sort(reverse=True)
        y_list.sort()
        for y in y_list:
            for x in x_list:
                coord.append([x, y, 0])
    elif case == "bottom-right" and grid_order_routing=='LR':
        x_list.sort(reverse=True)
        y_list.sort(reverse=True)
        for y in y_list:
            for x in x_list:
                coord.append([x, y, 0])
    elif case == "bottom-left" and grid_order_routing=='LR':
        x_list.sort()
        y_list.sort(reverse=True)
        for y in y_list:
            for x in x_list:
                coord.append([x, y, 0])
    elif case == 'top-left' and grid_order_routing=='UD':
        x_list.sort()
        y_list.sort()
        for x in x_list:
            for y in y_list:
                coord.append([x, y, 0])
    elif case == 'top-right' and grid_order_routing=='UD':
        x_list.sort(reverse=True)
        y_list.sort()
        for x in x_list:
            for y in y_list:
                coord.append([x, y, 0])
    elif case == "bottom-right" and grid_order_routing=='UD':
        x_list.sort(reverse=True)
        y_list.sort(reverse=True)
        for x in x_list:
            for y in y_list:
                coord.append([x, y, 0])
    elif case == "bottom-left" and grid_order_routing=='UD':
        x_list.sort()
        y_list.sort(reverse=True)
        for x in x_list:
            for y in y_list:
                coord.append([x, y, 0])
    return coord

def return_all_grid_points(case):  #retorna os pontos ordenados do grid para a modalidade alinhado
    index = routing_sequence()
    for i in range(index[0][0], index[0][1], index[0][2]):
        print("Etapa {} de {}".format(i,len(placas_locadas)))
        for j in range(index[1][0], index[1][1], index[1][2]):
            if placing_possible(i,j) == True:
                return all_grid_points(i,j,case)


def combinations_in_grid():  #verifica todas as combinações possíveis de grids nas dimensões de uma placa
    global panel_pix_x, panel_pix_y
    init_grid = []
    for i in range(0, panel_pix_y, 1):
        for j in range(0, panel_pix_x, 1):
            init_grid.append([i, j])
    return init_grid

def overall_score(p_list):  #soma dos scores das placas locadas
    os = 0
    for p in p_list:
        os += p.score
    return os

def overall_score_mean(p_list):  #média dos scores das placas locadas
    os = 0
    for p in p_list:
        os += p.score
    return os/len(p_list)

def return_placa_color(ident):  #retorna a cor de uma certa placa
    for placa in lista_placas:
        if placa.id == ident:
            return placa.color

def placas_img(c_index):  #gera a imagem das placas locadas a partir da matriz
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
    img1.save('output/{}-Placas_{}_orient-{}_{}placas.png'.format(c_index, routing, orient, placas_counter))
    img2 = Image.open('output/{}-Placas_{}_orient-{}_{}placas.png'.format(c_index, routing, orient, placas_counter))
    img0 = ImageDraw.Draw(img2)
    myFont = ImageFont.truetype('utilities/Roboto-Black.ttf', int(panel_pix_x/3))
    for placa in lista_placas:
        if panel_pix_x > 90:
            img0.text((placa.edges[0][0], placa.edges[0][1]), "{}".format(placa.id), font=myFont, fill=(0,0,0))
        else:
            img0.text((placa.edges[0][0], placa.edges[0][1]), "{}".format(placa.id), fill=(0,0,0))
    img2.save('output/{}-Placas_{}_orient-{}_{}placas-NUMBERED.png'.format(c_index, routing, orient, placas_counter))
    return soma


def area_de_interesse_img():  #gera imagem da área de interesse, apenas para debug
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


def where_looking_img():  #gera imagem do mapeamento da imagem, apenas para debug
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


def print_placas():  #imprime as placas locadas e suas propriedades
    global lista_placas
    print("------ Listagem das Placas ------")
    for placa in lista_placas:
        print("---- Placa {} ----".format(placa.id))
        print("Coordenadas:")
        print(" Top Left: x:{} y:{} z:{}".format(placa.coord[0].x, placa.coord[0].y, placa.coord[0].z))
        print(" Top Right: x:{} y:{} z:{}".format(placa.coord[1].x, placa.coord[1].y, placa.coord[1].z))
        print(" Bottom Left: x:{} y:{} z:{}".format(placa.coord[2].x, placa.coord[2].y, placa.coord[2].z))
        print(" Bottom Right: x:{} y:{} z:{}".format(placa.coord[3].x, placa.coord[3].y, placa.coord[3].z))
        print("Bordas em px: {}".format(placa.edges))
        print("Score: {}".format(placa.score))
    print("---------------------------------")


def panel_score(i, j):  #retorna o score de uma determinada placa
    global highest_sha_value, panel_pix_x, panel_pix_y
    cumulative_value = 0
    for u in range (i, i-panel_pix_y, -1):  #o menos é para detectar como bottom left
        for v in range (j, j+panel_pix_x, 1):
            cumulative_value += (highest_sha_value - heatmap[u][v])
    return (cumulative_value / (highest_sha_value*panel_pix_x*panel_pix_y))

def best_placing():  #nas modalidades livres, procura a próxima placa com o melhor score
    global placas_counter, lista_placas
    index = routing_sequence()
    best_score = 0
    cbp = [0, 0]  #current best place
    for i in range(index[0][0], index[0][1], index[0][2]):
        print("Etapa {} de {}".format(i,len(placas_locadas)))
        for j in range(index[1][0], index[1][1], index[1][2]):
            #print("Estamos no ponto {} {}".format(i,j))
            if placing_possible_in_shadow(i,j) == True:
                temp_score = panel_score(i,j)
                if temp_score > best_score:
                    best_score = temp_score
                    cbp = [i, j]
                elif temp_score == best_score:
                    print("Empate!")
    execute_placing(cbp[0],cbp[1], best_score)


def highest_score_position(grid_list):  #determina a posição de maior score dentro da lista de pontos do grid
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


"""Variáveis Globais"""
pix_x = None
pix_y = None
pix_area = None
pix_dens = 50

needed_placas = 100
placa_dim1 = 1.56
placa_dim2 = 0.70
esp_placa = 0.03
incl_pref = "Placa"  #Pode ser "Telhado" ou "Placa"
incl_value = 20   #em graus
incl_orient = '-y'
afastamento = 12 #em pixels
orient = "Hor"
routing = "top-left"
grid_order_routing = 'LR' #LR ou UD

axis_lock = False
orient_alternation = False



placa_dimx = None
placa_dimy = None

panel_pix_x = 11  #trocar depois nas funções
panel_pix_y = 21



"""Inicialização"""
#Ordem: orient, routing, axis_lock, orient_alternation

cases = [
#['Hor', 'top-left', False, False],
#['Hor', 'top-right', False, False],
#['Hor', 'bottom-left', False, False],
['Hor', 'top-left', False, False],
#['Vert', 'bottom-right', True, False],
#['Vert', 'bottom-right', False, True],
]

file_area = open('area', 'rb')
area_de_interesse = pickle.load(file_area)

file_heatmap = open('heatmap', 'rb')
heatmap = pickle.load(file_heatmap)
highest_sha_value = highest_value_in_array(heatmap)
print("O maior valor de sombreamento é {}".format(highest_sha_value))

#Proposta 01
"""
#execução de todos os casos
for case in cases:
    lista_placas = []
    placas_counter = 0
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
    print_placas()
    python_array_to_pickle(lista_placas, 'lista_placas')
"""

for case in cases:
    lista_placas = []
    placas_counter = 0
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
    print_placas()
    python_array_to_pickle(lista_placas, 'lista_placas')
    list_to_obj_file_new(lista_placas, esp_placa)
    print(overall_score_mean(lista_placas))
