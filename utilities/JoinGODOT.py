import math
import numpy as np
from BasicFunctions import *
import pickle
import csv
import os



def reshape_hmap_to_array(csv_filename):
	csvfile = open(csv_filename,'r')
	csvarray = csv.reader(csvfile, delimiter=',')
	item_counter = -1
	image_x = 0
	image_y = 0
	outarray_f = []
	outarray_l = []
	for row in csvarray:
		if item_counter >=0 and item_counter < image_x-1:
			value = int(row[3])
			if value == 0 or value == 1:
				outarray_l.append(-1)
			elif value == 2:
				outarray_l.append(0)
			elif value == 3:
				outarray_l.append(1)
			item_counter += 1
		elif item_counter >=0 and item_counter >= image_x-1:
			value = int(row[3])
			if value == 0 or value == 1:
				outarray_l.append(-1)
			elif value == 2:
				outarray_l.append(0)
			elif value == 3:
				outarray_l.append(1)
			outarray_f.append(outarray_l)
			outarray_l = []
			item_counter = 0
		elif item_counter == -1:
			image_x = int(row[0])
			image_y = int(row[1])
			item_counter += 1
	return outarray_f


def reshape_area_to_array(csv_filename):
	csvfile = open(csv_filename,'r')
	csvarray = csv.reader(csvfile, delimiter=',')
	item_counter = -1
	image_x = 0
	image_y = 0
	outarray_f = []
	outarray_l = []
	for row in csvarray:
		if item_counter >=0 and item_counter < image_x-1:
			value = int(row[3])
			if value == 0 or value == 1:
				outarray_l.append(None)
			elif value == 2 or value == 3:
				outarray_l.append(vec3(float(row[0]), float(row[1]), float(row[2])))
			item_counter += 1
		elif item_counter >=0 and item_counter >= image_x-1:
			value = int(row[3])
			if value == 0 or value == 1:
				outarray_l.append(None)
			elif value == 2 or value == 3:
				outarray_l.append(vec3(float(row[0]), float(row[1]), float(row[2])))
			outarray_f.append(outarray_l)
			outarray_l = []
			item_counter = 0
		elif item_counter == -1:
			image_x = int(row[0])
			image_y = int(row[1])
			item_counter += 1
	return outarray_f


def heatmap_files_sum(directory):
	filecounter = 0
	hmap_somado = None
	for filename in os.listdir(directory):
	    f = os.path.join(directory, filename)
	    if os.path.isfile(f):
	        if filecounter == 0:
	        	area = reshape_area_to_array(f)
	        	python_array_to_pickle(np.array(area), 'area')
	        	hmap_somado = np.array(reshape_hmap_to_array(f))
	        	filecounter += 1
	        else:
	        	hmap_somado += np.array(reshape_hmap_to_array(f))
	        	filecounter += 1
	    print("Arquivo {} somado".format(filecounter))     	
	print(hmap_somado[200])
	python_array_to_pickle(hmap_somado, 'heatmap')


heatmap_files_sum('input-GODOT')