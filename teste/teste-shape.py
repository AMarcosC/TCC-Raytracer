import os
import sys
import pandas as pd
import numpy as np
from descartes import PolygonPatch
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.getcwd()))
import alphashape

points_2d = [(0., 0.), (0., 1.), (1., 1.), (1., 0.),
          (0.5, 0.25), (0.5, 0.75), (0.25, 0.5), (0.75, 0.5)]

fig, ax = plt.subplots()
ax.scatter(*zip(*points_2d))
plt.savefig('figura-teste')
plt.show()

alpha_shape = alphashape.alphashape(points_2d)
print(alpha_shape)

fig, ax = plt.subplots()
ax.scatter(*zip(*points_2d))
ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2))
plt.savefig('figura-teste')
plt.show()
