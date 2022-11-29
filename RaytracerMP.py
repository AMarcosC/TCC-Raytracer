"""Notas da Versão 0.8"""
"""
Autor: Antônio Marcos Cruz da Paz - antonio.marcos@aluno.ufca.edu.br

- O que este código faz:
    - Cria uma imagem usando ray-tracing, a partir da interceptação de um raio com esferas em
    uma cena
    - Cria uma imagem usando ray-tracing, a partir da interceptação de um raio com  triângulos em
    uma cena
    - Aplica efeitos de difusão simples e de sombra opaca
    - Passa por várias horas do dia e posições diferentes do sol

- Ajustes pretendidos:
    - Retirar algumas comparações de distância de interceptação da função trace que parecem
    ser desnecessárias
    - Estudar não colocar a distância na matriz, apenas a cor

    "blender-cube-rotated.obj"

    - Trocar pixel pos (i,j) para (j,i)

    O eixo z no sentido positivo do programa é o eixo y negativo do blender, espelhado

    Press R to rotate, press Y to snap to the Y-axis, and enter -90 on your keyboard
     to rotate an object -90 degrees on the Y-axis
     R + X + 90
"""

"""Bibliotecas"""

import os
import sys
from OBJFileParser import parse
from BasicFunctions import *
import math
import numpy as np
from PIL import Image
from numpy import linalg
from colour import Color
import pickle
import multiprocessing
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from tqdm import tqdm
import yaml

"""Funções Voltadas ao problema"""


def ray_p(t,e,dir):  #fórmula que define o ponto no espaço atingido por um raio
    p = e + vetor_escalar(dir,t)
    return p

# we advance from e along the vector (s − e) a
# fractional distance t to find the point p.
# e = origem do raio
# p = ponto de intersecção
# s - e = direção do raio (d)
# t = fração de distância

def pixel_pos(i,j):  #transforma um pixel na tela em um ponto no espaço
    u = l + ((r-l)*(i+0.5))/n_x  #0,5 para centralizar o ponto no pixel
    v = top + ((bot-top)*(j+0.5))/n_y  #0,5 para centralizar o ponto no pixel
    return([u, v])


def screen_size(list_triangles):  #deterimina o tamamho da tela (descontinuada)
    global l, r, top, bot, depth, n_x, n_y, pixel_por_metro
    x_menor = FARAWAY
    x_maior = - FARAWAY
    y_menor = FARAWAY
    y_maior = - FARAWAY
    z_maior = - FARAWAY
    for triangle in list_triangles:
        for vertex in triangle.v:
            if vertex.x > x_maior:
                x_maior = vertex.x
            if vertex.x < x_menor:
                x_menor = vertex.x
            if vertex.y > y_maior:
                y_maior = vertex.y
            if vertex.y < y_menor:
                y_menor = vertex.y
            if vertex.z > z_maior:
                z_maior = vertex.z
    l = (int((x_menor)*1.2)) - 1
    r = (int((x_maior)*1.2)) + 1
    top = (int((y_maior)*1.2)) + 1
    bot = (int((y_menor)*1.2)) - 1
    if z_maior <= 0:
        depth = 1
    else:
        depth = int(z_maior) + 1
    n_x = abs(r-l)*pixel_por_metro
    n_y = abs(top-bot)*pixel_por_metro


def screen_size_forr(list_triangles):  #determina o tamanho da tela
    global l, r, top, bot, depth, n_x, n_y, pixel_por_metro, forramento
    x_menor = FARAWAY
    x_maior = - FARAWAY
    y_menor = FARAWAY
    y_maior = - FARAWAY
    z_maior = - FARAWAY
    for triangle in list_triangles:
        for vertex in triangle.v:
            if vertex.x > x_maior:
                x_maior = vertex.x
            if vertex.x < x_menor:
                x_menor = vertex.x
            if vertex.y > y_maior:
                y_maior = vertex.y
            if vertex.y < y_menor:
                y_menor = vertex.y
            if vertex.z > z_maior:
                z_maior = vertex.z
    l = math.floor(int((x_menor)-(forramento))) - 1
    r = math.ceil(int((x_maior)+(forramento))) + 1
    top = math.ceil(int((y_maior)+(forramento))) + 1
    bot = math.floor(int((y_menor)-(forramento))) - 1
    if z_maior <= 0:
        depth = 1
    else:
        depth = int(z_maior) + 1
    n_x = abs(r-l)*pixel_por_metro
    n_y = abs(top-bot)*pixel_por_metro


def intersect_sph(e,esfera): #função que determina se um vetor intercepta uma esfera (retorna cor e distância)
    raiz = ((dir.dot((e-esfera.c)))**2) - ((dir.dot(dir))*(((e-esfera.c).dot((e-esfera.c))) - ((esfera.r)**2)))
    if raiz > 0:
        t1 = (-(dir.dot((e-esfera.c))) + np.sqrt(raiz))/(dir.dot(dir))
        t2 = (-(dir.dot((e-esfera.c))) - np.sqrt(raiz))/(dir.dot(dir))
        if (t1 >=0 and t1 < FARAWAY) or (t2 >= 0 and t2 < FARAWAY):
            return (esfera.color, menor(t1,t2))
        else:
            return ([0,0,0,0], FARAWAY)
    else:
        return ([0,0,0,0], FARAWAY)


def intersect_sph_bool(e,esfera,luz_dir): #função que determina se um vetor intercepta uma esfera (retorna um booleano)
    raiz = ((luz_dir.dot((e-esfera.c)))**2) - ((luz_dir.dot(luz_dir))*(((e-esfera.c).dot((e-esfera.c))) - ((esfera.r)**2)))
    if raiz >= 0:
        t1 = (-(luz_dir.dot((e-esfera.c))) + np.sqrt(raiz))/(luz_dir.dot(luz_dir))
        t2 = (-(luz_dir.dot((e-esfera.c))) - np.sqrt(raiz))/(luz_dir.dot(luz_dir))
        if (t1 > 0 and t1 < FARAWAY) or (t2 > 0 and t2 < FARAWAY):   #refinar depois
            return True
        else:
            return False
    else:
        return False


def intersect_sph_coord(e,esfera):  #função que determina a coordenada de inteceptação em uma esfera - NÃO UTILIZADA, PORÉM ÚTIL
    raiz = ((dir.dot((e-esfera.c)))**2) - ((dir.dot(dir))*(((e-esfera.c).dot((e-esfera.c))) - ((esfera.r)**2)))
    if raiz > 0:
        t1 = (-(dir.dot((e-esfera.c))) + np.sqrt(raiz))/(dir.dot(dir))
        t2 = (-(dir.dot((e-esfera.c))) - np.sqrt(raiz))/(dir.dot(dir))
        if t1 >= 0 and t2 >=0:
            tf = menor(t1,t2)
            return ray_p(tf,e,dir)
        elif t1 >= 0 and t2 <0:
            return ray_p(t1,e,dir)
        elif t1 < 0 and t2 >=0:
            return ray_p(t2,e,dir)
        else:
            print("Erro")

def diffuse_sph(int_point, esfera, dir_luz, kd, ka):  #função que retorna a cor do pixel devido ao efeito de difusão
    n = normal_sph(int_point, esfera)
    l = dir_luz
    f = n.dot(l)
    if f >= 0:
        red = (ka*esfera.color[0]) + (kd*f*esfera.color[0])
        green = (ka*esfera.color[1]) + (kd*f*esfera.color[1])
        blue = (ka*esfera.color[2]) + (kd*f*esfera.color[2])
        return ([red,green,blue,255])
    else:
        red = (ka*esfera.color[0]) + (kd*(0)*esfera.color[0])
        green = (ka*esfera.color[1]) + (kd*(0)*esfera.color[1])
        blue = (ka*esfera.color[2]) + (kd*(0)*esfera.color[2])
        return ([red,green,blue,255])

def intercept_tri(tri, e, d):  #função que define a interceptação de um triângulo por um raio
    v1 = tri.v[0]  #vértice de um triângulo
    v2 = tri.v[1]  #vértice de um triângulo
    v3 = tri.v[2]  #vértice de um triângulo
    a = [
    [v1.x - v2.x, v1.x - v3.x, d.x],
    [v1.y - v2.y, v1.y - v3.y, d.y],
    [v1.z - v2.z, v1.z - v3.z, d.z],
    ]
    b = [(v1.x - e.x), (v1.y - e.y), (v1.z - e.z)]
    if linalg.det(a) != 0:
        x = linalg.solve(a, b)
        if x[0] > 0 and x[1] > 0 and (x[0]+x[1] < 1) and x[2] > 0 and x[2] < FARAWAY:
            return (tri.color, x[2])
        else:
            return ([0,0,0,0], FARAWAY)
    else:
        return ([0,0,0,0], FARAWAY)


def intercept_tri_bool(tri, e, d): #função que define a interceptação de um triângulo por um raio (retorna um booleano)
    v1 = tri.v[0]
    v2 = tri.v[1]
    v3 = tri.v[2]
    a = [
    [(v1.x - v2.x), (v1.x - v3.x), (d.x)],
    [(v1.y - v2.y), (v1.y - v3.y), (d.y)],
    [(v1.z - v2.z), (v1.z - v3.z), (d.z)],
    ]
    b = [(v1.x - e.x), (v1.y - e.y), (v1.z - e.z)]
    if linalg.det(a) != 0:
        x = linalg.solve(a, b)
        if x[0] > 0 and x[1] > 0 and (x[0]+x[1] < 1) and x[2] > 0 and x[2] < FARAWAY:
            return True
        else:
            return False
    else:
        return False

def obj_to_triangles(list, color):  #traz o arquivo obj e coloca os triângulos no formato da classe utilizada pelo programa
    list_triangles = []
    for face in list:
        v1 = vec3(face[0][0],face[0][1], face[0][2])
        v2 = vec3(face[1][0],face[1][1], face[1][2])
        v3 = vec3(face[2][0],face[2][1], face[2][2])
        normal = vec3(face[3][0], face[3][1], face[3][2])
        face_atual = Triangle(v1, v2, v3, color, normal)
        list_triangles.append(face_atual)
    return list_triangles

def add_triangles_to_cena(list_triangles):  #adiciona os triângulos na cena
    for triangle in list_triangles:
        cena.append(triangle)

def diffuse_tri(tri, dir_luz, kd, ka):  #define a cor do triângulo devido ao efeito de difusão
    n = tri.normal
    l = dir_luz
    f = n.dot(l)
    if f >= 0:
        red = (ka*tri.color[0]) + (kd*f*tri.color[0])
        green = (ka*tri.color[1]) + (kd*f*tri.color[1])
        blue = (ka*tri.color[2]) + (kd*f*tri.color[2])
        return ([red,green,blue,255])
    else:
        red = (ka*tri.color[0]) + (kd*(0)*tri.color[0])
        green = (ka*tri.color[1]) + (kd*(0)*tri.color[1])
        blue = (ka*tri.color[2]) + (kd*(0)*tri.color[2])
        return ([red,green,blue,255])


def trace_sph(): #função que emite os raios para um círculo
    table = []  #matriz vazia
    for i in range (0, n_y, 1):  #passando pelos pixels verticalmente
        line = []    #lista vazia
        for j in range (0, n_x, 1):  #passando pelos pixels horizontalmente
                et = pixel_pos(j,i)  #determina o ponto do pixel no espaço (origem da luz)
                e = vec3(et[0],et[1], depth)  #a origem do raio é o ponto do pixel no espaço
                res = ([0,0,0,0], FARAWAY)  #o pixel inicia as iterações como transparente e no infinito
                for objeto in cena:  #pra cada objeto na cena
                    temp = intersect_sph(e,objeto) #função que determina se o raio intercepta a esfera no espaço
                    if temp[1] < res[1]:  #se a distância da interceptação temp[1] for menor que a distância atual res[1]
                        intercept_point = ray_p(temp[1],e,dir)  #descobrimos o ponto dessa interceptação no espaço
                        temp = (diffuse_sph(intercept_point, objeto, luz_dir, kd, ka),temp[1])  #aplicamos a cor resultante do efeito de difusão, e mantemos a distância
                        if temp[1] <= res[1]:  #se a distância da interceptação temp[1] for menor que a distância atual res[1] - ESTUDAR RETIRAR
                            res = temp         #Estudar retirar, parece desnecessário
                        for outro_obj in cena: #para os objetos na cena
                            if outro_obj != objeto and intersect_sph_bool(intercept_point,outro_obj,luz_dir): #se o objeto não for ele mesmo e interceptar outra esfera
                                if temp[1] <= res[1]:  #e a distância dessa interceptação for menor ou igual que a atual
                                    res = ([0,0,0,255], temp[1])  #então este pixel está na sombra
                line.append(res[0])     #adiciona o valor da cor interceptada na lista
        print("{} de {}".format(i, n_y))       #indica o andamento
        table.append(line)           #adiciona a lista na matriz, para compor a imagem
    return table  #retorna a tabela com as cores


def trace_tri(): #função que emite os raios para um conjunto de triângulos
    coord_list = all_combinations(n_y, n_x)
    resultados = trace_tri_results()
    print("---Passando Resultados---")
    res_ar = list_to_array_reshape(resultados, n_x, n_y)
    return res_ar


def trace_tri_results(): #função que emite os raios para um conjunto de triângulos
    coord_list = all_combinations(n_y, n_x)
    pbar_trace = tqdm(total=len(coord_list))
    resultados_list = []
    pool = Pool(processes=core_count-1)  #aumentar ou diminuir depois
    for result in pool.imap(color_on_point_pre_mapped, coord_list, chunksize=n_x):
        resultados_list.append(result)
        pbar_trace.update(1)
    pool.close() # No more work
    pool.join() # Wait for completion
    return resultados_list  #retorna a lista com as cores, precisa ser colocada em shape


def color_on_point(c):  #determina a cor em um certo pixel da imagem, baseada no objeto que está nele
    et = pixel_pos(c[1],c[0])  #determina o ponto do pixel no espaço (origem da luz)
    e = vec3(et[0],et[1], depth)  #a origem do raio é o ponto do pixel no espaço
    res = ([0,0,0,0], FARAWAY)  #o pixel inicia as iterações como transparente e no infinito
    for objeto in cena:  #pra cada objeto na cena
        temp = intercept_tri(objeto, e, dir)
        if temp[1] < res[1]:  #se a distância da interceptação temp[1] for menor que a distância atual res[1]
            res = temp
            intercept_point = ray_p(res[1],e,dir)  #descobrimos o ponto dessa interceptação no espaço
            temp = (diffuse_tri(objeto, luz_dir, kd, ka),temp[1])  #aplicamos a cor resultante do efeito de difusão, e mantemos a distância
            if temp[1] <= res[1]:  #se a distância da interceptação temp[1] for menor que a distância atual res[1] - ESTUDAR RETIRAR
                res = temp         #Estudar retirar, parece desnecessário
            for outro_obj in cena: #para os objetos na cena
                if outro_obj != objeto and intercept_tri_bool(outro_obj, intercept_point,luz_dir): #se estivermos no telhado, se o triângulo não for ele mesmo e interceptar outro triângulo
                    res = ([0,0,0,255], temp[1])  #então este pixel está na sombra
    return res[0]     #adiciona o valor da cor interceptada na lista


def color_on_point_pre_mapped(c):  #determina a cor de um certo pixel, para o caso do pré-mapeamento de objetos
    ponto = pre_mapped[c[0]][c[1]]
    if ponto[0] == None:
        return [0,0,0,0]
    else:
        intercept_point = ponto[0]
        temp = (diffuse_tri(cena[ponto[1]], luz_dir, kd, ka))  #aplicamos a cor resultante do efeito de difusão, e mantemos a distância
        for outro_obj in modelagem: #para os objetos na cena
            if outro_obj != cena[ponto[1]] and intercept_tri_bool(outro_obj, intercept_point,luz_dir): #se estivermos no telhado, se o triângulo não for ele mesmo e interceptar outro triângulo
                temp = [0,0,0,255] #então este pixel está na sombra
        return temp     #adiciona o valor da cor interceptada na lista


def shadow_to_heatmap(tabela):  #transforma os pontos sombreados em uma matriz cujos valores determinam a intensidade do sombreamento
    tabela_return = []
    for i in range (0, len(tabela)):
        linha_return = []
        for j in range (0, len(tabela[0])):
            if area_de_interesse[i][j] != None:
                if tabela[i][j] == [0,0,0,255]:
                    linha_return.append(1)
                else:
                    linha_return.append(0)
            else:
                linha_return.append(-1)
        tabela_return.append(linha_return)
    return tabela_return


def heatmap_to_img(heatmap):  #transforma a matriz dos valores de sombreamento em uma imagem (campo escalar)
    numero_cores = len(heatmap)+1
    colors = color_range(numero_cores)
    soma = np.zeros((n_y,n_x))
    img = []
    for time in heatmap:
        soma = soma + time
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


def pixel_coordinates(n, m):  #determina as coordenadas reais dos pixels da tela
    tabela_pc = []
    for i in range (0,n,1):
        linha_pc = []
        for j in range (0,m,1):
            x_y = pixel_pos(j,i)
            z = depth
            linha_pc.append(vec3(x_y[0], x_y[1], z))
        tabela_pc.append(linha_pc)
    return tabela_pc

def area_of_interest():   #retorna uma matriz com apenas os pontos da área de interesse, vec3
    coord_list = all_combinations(n_y, n_x)
    resultados = area_of_interest_results()
    print("---Passando Resultados---")
    res_ar = list_to_array_reshape(resultados, n_x, n_y)
    return res_ar


def area_of_interest_results():   #retorna uma matriz com apenas os pontos da área de interesse, vec3  (descontinuada)
    coord_list = all_combinations(n_y, n_x)
    resultados_list = []
    print("---Delimitando área de interesse---")
    pbar = tqdm(total=len(coord_list))
    pool = Pool(processes=core_count-1)  #aumentar ou diminuir depois
    results = pool.imap(area_of_interest_check, coord_list, chunksize=n_x)
    for result in results:
        resultados_list.append(result)
        pbar.update(1)
    pool.close() # No more work
    pool.join() # Wait for completion
    return resultados_list  #analisar necessidade


def area_of_interest_check(c):  #retorna o ponto de interceptação para formar a área de interesse  (descontinuada)
    intercept_point = None
    pos_ini = coordenadas_pixels[c[0]][c[1]]
    dist_atual = FARAWAY
    for objeto in cena:
        temp = intercept_tri(objeto, pos_ini, dir)
        if temp[1] < dist_atual and (objeto in telhado):  #se a distância da interceptação temp[1] for menor que a distância atual e estiver no telhado
            dist_atual = temp[1]
            intercept_point = ray_p(dist_atual,pos_ini,dir) #descobrimos o ponto dessa interceptação no espaço
    return intercept_point


def object_pre_mapping():   #retorna uma matriz com os objetos tocados pelo primeiro raio emitido
    coord_list = all_combinations(n_y, n_x)
    resultados = object_pre_mapping_results()
    print("---Passando Resultados---")
    res_ar = list_to_array_reshape(resultados, n_x, n_y)
    return res_ar


def object_pre_mapping_results():   #cria um pool de processos para procurar os objetos tocados pelo primeiro raio emitido
    coord_list = all_combinations(n_y, n_x)
    resultados_list = []
    print("---Pré Mapeando Objetos---")
    pbar = tqdm(total=len(coord_list))
    pool = Pool(processes=core_count-1)  #aumentar ou diminuir depois
    results = pool.imap(object_pre_mapping_check, coord_list, chunksize=n_x)
    for result in results:
        resultados_list.append(result)
        pbar.update(1)
    pool.close() # No more work
    pool.join() # Wait for completion
    return resultados_list  #analisar necessidade


def object_pre_mapping_check(c):  #verifica qual é o objeto tocado pelo raio emitido em um certo ponto da tela
    intercept_point = None
    pos_ini = coordenadas_pixels[c[0]][c[1]]
    dist_atual = FARAWAY
    obj_atual = None
    for objeto in cena:
        temp = intercept_tri(objeto, pos_ini, dir)
        if temp[1] < dist_atual:  #se a distância da interceptação temp[1] for menor que a distância atual e estiver no telhado
            dist_atual = temp[1]
            intercept_point = ray_p(dist_atual,pos_ini,dir) #descobrimos o ponto dessa interceptação no espaço
            obj_atual = cena.index(objeto)
    return [intercept_point, obj_atual, dist_atual]


def color_range(n_colors):  #cria a faixa de cores usada na imagem do mapa de calor
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

def area_of_interest_from_pre_mapping():  #obtém a aŕea de interesse a partir do pré-mapeamento de objetos (a forma antiga foi descontinuada)
    tt = np.full((n_y, n_x), None)
    for i in range (0, len(pre_mapped), 1):
        for j in range (0, len(pre_mapped[0]), 1):
            c_t = pre_mapped[i][j]
            if c_t[1] != None:
                if cena[c_t[1]] in telhado:
                    tt[i][j] = c_t[0]
    return tt

"""Variáveis Globais e Locais"""
core_count=multiprocessing.cpu_count()
print("Número de núcleos da CPU: {}".format(core_count))

with open('Raytracer-Config.yaml', "r") as c_file:
    cf = yaml.safe_load(c_file)
print(cf)


offset = cf['MODELO']['OFFSET']
pixel_por_metro = cf['GERAL']['DENSIDADE_PIXEL']
forramento = cf['MODELO']['FORRAMENTO']
FARAWAY = 1.0e39
depth = 10  #profundidade da tela em relação à origem

kd = cf['GERAL']['K_D']  #coeficiente de difusão
ka = cf['GERAL']['K_A']  #coeficiente de ambiente

n_x = 200  #(tamaho da tela em x)
n_y = 150  #tamanho da tela em y)
l = -4    #coordenada x da esquerda da tela
r = 4    #coordenada x da direita da tela
top = 3  #coordenada y do topo da tela
bot = -3  #coordenada y do fim da tela


change_to_current_dir()
telhado_obj = parse(cf['MODELO']['AREA_DE_INTERESSE_OBJ'])
modelagem_obj = parse(cf['MODELO']['MODELAGEM_OBJ'])
cena = []
telhado = obj_to_triangles(telhado_obj, cf['MODELO']['AREA_DE_INTERESSE_COR'])
modelagem = obj_to_triangles(modelagem_obj, cf['MODELO']['MODELAGEM_COR'])

add_triangles_to_cena(telhado)
add_triangles_to_cena(modelagem)

screen_size_forr(cena)

print(n_x, n_y)

dir = vec3(0,0,-1) #direção dos raios lançados pela tela
# a direção "d" do raio é sempre -w [0,0,-1] (vetor unitário)

luz_dir = vec3(-0.6247,0.6247,0.46852)  #direção da origem até a luz, unitário


#fonte: https://www.sunearthtools.com/dp/tools/pos_sun.php?lang=pt
sunpath = cf['TRAJETORIA']

"""Inicialização"""
cont = 0
heatmap = []
shape_points = []  #testando apenas

coordenadas_pixels = pixel_coordinates(n_y,n_x)
coordenadas_intercept = []

#tab_area_of_interest_base = multiprocessing.Array()   #estudar retirar essa linha

pre_mapped = object_pre_mapping()
#area_de_interesse = area_of_interest()  #area_de_interesse: matriz de coordenadas em vec3
area_de_interesse = area_of_interest_from_pre_mapping()
table = np.full((n_y, n_x), None)  #matriz vazia



for time in sunpath:
    cont = cont+1
    print("----- Etapa {} de {} ------".format(cont,len(sunpath)))
    luz_dir = polar_to_vector_ajustado(time[0], time[1], offset)
    tabela1 = trace_tri()  #transcreve os raios emitidos e a sua resposta em uma matriz
    heatmap.append(shadow_to_heatmap(tabela1))
    img1 = Image.fromarray(np.uint8(tabela1)).convert('RGBA')  #Transformando a matriz em uma imagem .png
    img1.save('output/MRay_Teste{}.png'.format(cont))

#print(heatmap)


heatmap_somado = heatmap_to_img(heatmap)
#print(heatmap_somado)

python_array_to_pickle(heatmap_somado, 'heatmap')
python_array_to_pickle(area_de_interesse, 'area')


print("---------------Terminou-------------------")
