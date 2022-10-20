from PIL import Image
from colour import Color
from PIL import ImageDraw
from PIL import ImageFont
from BasicFunctions import *

def color_range(n_colors):
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

cr=color_range(32)
color_range_image(cr)
