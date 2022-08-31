"""
Este arquivo condensa funções e classes básicas para o funcionamento do programa, sendo funções que não
se relacionam diretamente com o problema do ray-tracing
"""

import os
import math
import numpy as np
import sys
import pickle
from PIL import Image

"""Classes"""

class vec3():  #classe que define o funcionamento de um vetor e suas operações
    def __init__(self, x, y, z):
        (self.x, self.y, self.z) = (x, y, z)
    def __mul__(self, other):
        return vec3(self.x * other, self.y * other, self.z * other)
    def __add__(self, other):
        return vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other):
        return vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    def dot(self, other):
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)
    def __abs__(self):
        return self.dot(self)
    def norm(self):
        mag = np.sqrt(abs(self))
        return self * (1.0 / np.where(mag == 0, 1, mag))
    def components(self):
        return (self.x, self.y, self.z)
    def extract(self, cond):
        return vec3(extract(cond, self.x),
                    extract(cond, self.y),
                    extract(cond, self.z))
    def place(self, cond):
        r = vec3(np.zeros(cond.shape), np.zeros(cond.shape), np.zeros(cond.shape))
        np.place(r.x, cond, self.x)
        np.place(r.y, cond, self.y)
        np.place(r.z, cond, self.z)
        return r

class Sphere:  #classse que define as propriedades de uma esfera
    def __init__(self, center, r, color):
        self.c = center
        self.r = r
        self.color = color

class Objeto:  #classse que define as propriedades de um objeto genérico qualquer
    def __init__(self, file, color):
        self.f = file
        self.color = color

class Triangle:  #classe que define as propriedades de um triângulo
    def __init__(self, v1, v2, v3, color, normal = vec3(0,0,1)):
        self.v = [v1, v2, v3]
        self.color = color
        self.normal = normal

class Point:  #classe que define um ponto (não utilizada pq a vec3 é mais completa)
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

"""Funções Básicas"""

def vetor_escalar(vetor,escalar): #multiplicação de um vetor por um escalar
    comp_x = vetor.x * escalar
    comp_y = vetor.y * escalar
    comp_z = vetor.z * escalar
    return(vec3(comp_x,comp_y,comp_z))  #retorna o valor como vec3 (classe)

def menor(x1,x2):  #retorna o menor valor entre dois valores
    if x1 <= x2:
        return x1
    else:
        return x2

def menor_absoluto(x1,x2):  #retorna o menor valor absoluto entre dois valores (com sinal)
    if abs(x1) <= abs(x2):
        return x1
    else:
        return x2

def mais_proximo(x1,x2,dir):  #retorna a interseção mais próxima em um objeto (dir em vec3)
    if dir.z > 0:
        if x1 >= x2:
            return x1
        else:
            return x2
    else:
        if x1 >= x2:
            return x2
        else:
            return x1


def normal_sph(e,esfera):  #define o vetor normal unitário à superfície de uma esfera
    normal_x = (e.x - esfera.c.x)/esfera.r
    normal_y = (e.y - esfera.c.y)/esfera.r
    normal_z = (e.z - esfera.c.z)/esfera.r
    return vec3(normal_x, normal_y, normal_z)

def azimuth(angle):  #converte o ângulo no sistema trigonométrico para o de azimute
    if angle >= 0 and angle < 90:
        return (90 - angle)
    elif angle >= 90 and angle < 180:   #ajeitar depois
        return (360 - (angle - 90))
    elif angle >= 180 and angle < 270:  #ajeitar depois
        return (270 - angle + 180)
    elif angle >= 270 and angle < 360:
        return (360 - angle + 90)

def polar_to_vector(el,az):  #converte as coordenadas polares do sol em um vetor unitário (não utilizada, corrigida na função seguinte)
    x = math.cos(math.radians(el))*math.cos(math.radians(az))
    y = math.cos(math.radians(el))*math.sin(math.radians(az))
    z = math.sin(math.radians(el))
    return vec3(x, y, z)

def polar_to_vector_ajustado(el,az):  #converte as coordenadas polares do sol em um vetor unitário, considerando azimute com 0° no norte e sentido horário
    az_ajustado = azimuth(az)
    x = math.cos(math.radians(el))*math.cos(math.radians(az_ajustado))
    y = math.cos(math.radians(el))*math.sin(math.radians(az_ajustado))
    z = math.sin(math.radians(el))
    return vec3(x, y, z)


def change_to_current_dir():  #muda a pasta de trabalho atual (apenas para debug)
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

def vec3_array_to_python_array(array):
    new_array=np.full_like(array, None)
    for i in range (0, len(array), 1):
        for j in range (0, len(array[0]), 1):
            if array[i][j] != None:
                new_array[i][j] == [array[i][j].x, array[i][j].y, array[i][j].z]
    return new_array

def python_array_to_pickle(array, filename):
    file = open(filename, 'wb')
    pickle.dump(array, file)
    file.close()

def random_color():
    color = list(np.random.choice(range(256), size=3))
    return ([color[0], color[1], color[2], 255])

def overlay_images(front_image, back_image, final_image):
    img1 = Image.open(front_image)
    img1 = img1.convert("RGBA")
    img2 = Image.open(back_image)
    img2 = img2.convert("RGBA")
    new_img = Image.blend(img2, img1, 0.5)
    new_img.save(final_image,"PNG")
