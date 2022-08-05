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


def intersect_sph_coord(e,esfera): #função que determina a coordenada de inteceptação em uma esfera - NÃO UTILIZADA, PORÉM ÚTIL
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

def diffuse_tri(int_point, tri, dir_luz, kd, ka):  #define a cor do triângulo devido ao efeito de difusão  #retirar int_point
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
    table = []  #matriz vazia
    for i in range (0, n_y, 1):  #passando pelos pixels verticalmente
        line = []    #lista vazia
        for j in range (0, n_x, 1):  #passando pelos pixels horizontalmente
                et = pixel_pos(j,i)  #determina o ponto do pixel no espaço (origem da luz)
                e = vec3(et[0],et[1], depth)  #a origem do raio é o ponto do pixel no espaço
                res = ([0,0,0,0], FARAWAY)  #o pixel inicia as iterações como transparente e no infinito
                for objeto in cena:  #pra cada objeto na cena
                    temp = intercept_tri(objeto, e, dir)
                    if temp[1] < res[1]:  #se a distância da interceptação temp[1] for menor que a distância atual res[1]
                        res = temp
                        intercept_point = ray_p(res[1],e,dir)  #descobrimos o ponto dessa interceptação no espaço
                        temp = (diffuse_tri(intercept_point, objeto, luz_dir, kd, ka),temp[1])  #aplicamos a cor resultante do efeito de difusão, e mantemos a distância
                        if temp[1] <= res[1]:  #se a distância da interceptação temp[1] for menor que a distância atual res[1] - ESTUDAR RETIRAR
                            res = temp         #Estudar retirar, parece desnecessário
                        for outro_obj in cena: #para os objetos na cena
                            if outro_obj != objeto and intercept_tri_bool(outro_obj, intercept_point,luz_dir): #se estivermos no telhado, se o triângulo não for ele mesmo e interceptar outro triângulo
                                #if temp[1] <= res[1]:  #e a distância dessa interceptação for menor ou igual que a atual
                                res = ([0,0,0,255], temp[1])  #então este pixel está na sombra
                line.append(res[0])     #adiciona o valor da cor interceptada na lista
        print("{} de {}".format(i, n_y))       #indica o andamento
        table.append(line)           #adiciona a lista na matriz, para compor a imagem
    return table  #retorna a tabela com as cores



def shadow_to_heatmap(tabela):  #transforma os valores do vetor heatmap em uma tabela de cores
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


def heatmap_to_img(heatmap):
    initial_color = Color("green")
    colors = list(initial_color.range_to(Color("red"),len(heatmap)+1))
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
    return soma


def pixel_coordinates(n, m):
    tabela_pc = []
    for i in range (0,n,1):
        linha_pc = []
        for j in range (0,m,1):
            x_y = pixel_pos(j,i)
            z = depth
            linha_pc.append(vec3(x_y[0], x_y[1], z))
        tabela_pc.append(linha_pc)
    return tabela_pc

def area_of_interest(pixel_positions):   #retorna
    tab_area_of_interest = np.full_like(pixel_positions, None)
    print("---Delimitando área de interesse---")
    for i in range (0, len(pixel_positions), 1):
        for j in range (0, len(pixel_positions[0]), 1):
            pos_ini = pixel_positions[i][j]
            dist_atual = FARAWAY
            for objeto in cena:
                temp = intercept_tri(objeto, pos_ini, dir)
                if temp[1] < dist_atual and (objeto in telhado):  #se a distância da interceptação temp[1] for menor que a distância atual e estiver no telhado
                    dist_atual = temp[1]
                    intercept_point = ray_p(dist_atual,pos_ini,dir)  #descobrimos o ponto dessa interceptação no espaço
                    tab_area_of_interest[i][j] = intercept_point
    return tab_area_of_interest

def create_shape(intensity):
    if intensity < 0 and intensity > len(heatmap):
        print('Não há região com a intensidade determinada!')
    for i in range (0,len(area_de_interesse),1):
        for j in range (0,len(area_de_interesse[0]),1):
            vect = area_de_interesse[i][j]
            if vect != None and heatmap_somado[i][j] == intensity:
                shape_points.append(vect)
                print("x:{} y:{}".format(vect.x, vect.y))



"""Variáveis Globais e Locais"""

FARAWAY = 1.0e39  #uma distância grande
depth = 10  #profundidade da tela em relação à origem

kd = 0.6  #coeficiente de difusão
ka = 0.4  #coeficiente de ambiente

n_x = 200  #(tamaho da tela em x)
n_y = 150  #tamanho da tela em y)
l = -4    #coordenada x da esquerda da tela
r = 4    #coordenada x da direita da tela
top = 3  #coordenada y do topo da tela
bot = -3  #coordenada y do fim da tela



tri2 = Triangle(vec3(-60,45,-25), vec3(-60,-45,-25), vec3(60,-45,-25), [255, 255, 255, 255]) #fundo da imagem (branco)
tri3 = Triangle(vec3(-60,45,-25), vec3(60,45,-25), vec3(60,-45,-25), [255, 255, 255, 255])   #fundo da imagem (branco)

os.chdir(sys.path[0])
print(os.listdir())
change_to_current_dir()
telhado_obj = parse('assets/Telhado-Telhado.obj')
modelagem_obj = parse('assets/Telhado-Parede.obj')
cena = [tri2, tri3]
telhado = obj_to_triangles(telhado_obj, [217,101,78,255])
modelagem = obj_to_triangles(modelagem_obj, [97,83,80,255])

add_triangles_to_cena(telhado)
add_triangles_to_cena(modelagem)


dir = vec3(0,0,-1) #direção dos raios lançados pela tela
# a direção "d" do raio é sempre -w [0,0,-1] (vetor unitário)

luz_dir = vec3(-0.6247,0.6247,0.46852)  #direção da origem até a luz, unitário

eps = 0.00025  #uma distância para afastar o ponto do próprio objeto
#para evitar auto-detecção

#fonte: https://www.sunearthtools.com/dp/tools/pos_sun.php?lang=pt
sunpath = [
#[-0.8330, 73.97],
#[4.18,	73.26],
#[18.33, 70.43],
#[32.15,	65.89],
#[45.34,	58.37],
#[57.08,	44.88],
#[65.24,	19.86],
#[65.84,	344.63],
#[58.45,	317.74],
[47.01,	303.09],
#[33.96,	295],
#[20.2, 290.18],
#[6.09, 287.18],
#[-0.833, 286.17]
]

"""Inicialização"""
cont = 0
heatmap = []
shape_points = []  #testando apenas

coordenadas_pixels = pixel_coordinates(n_y,n_x)
coordenadas_intercept = []
area_de_interesse = area_of_interest(coordenadas_pixels)  #area_de_interesse: matriz de coordenadas em vec3

for time in sunpath:
    cont = cont+1
    print("----- Etapa {} de {} ------".format(cont,len(sunpath)))
    luz_dir = polar_to_vector_ajustado(time[0], time[1])
    tabela1 = trace_tri()  #transcreve os raios emitidos e a sua resposta em uma matriz
    heatmap.append(shadow_to_heatmap(tabela1))
    img1 = Image.fromarray(np.uint8(tabela1)).convert('RGBA')  #Transformando a matriz em uma imagem .png
    img1.save('output/MRay_Teste{}.png'.format(cont))

print(heatmap)

heatmap_somado = heatmap_to_img(heatmap)

create_shape(0)

print("---------------Terminou-------------------")
