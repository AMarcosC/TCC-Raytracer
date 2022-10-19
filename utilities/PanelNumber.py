import numpy as np
import math
from BasicFunctions import *
from colour import Color
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

change_to_current_dir()

file_placas = open('lista_placas', 'rb')
placas = pickle.load(file_placas)
print(placas)

nome_imagem = r"0-Placas_bottom-left_orient-Vert_29placas.png"

myFont = ImageFont.truetype('Roboto-Black.ttf', 65)

img2 = Image.open(nome_imagem)
img0 = ImageDraw.Draw(img2)
for placa in placas:
    img0.text((placa.edges[0][0], placa.edges[0][1]), "{}".format(placa.id), font=myFont,fill=(0,0,0))
img2.save('NUMBERED.png')
