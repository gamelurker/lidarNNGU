# -*- coding: utf-8 -*-
"""check_distance_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wDFIxXLJa2ILlkSgpKkG0rR8MFful44Y
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 21:50:44 2022

@author: Vadim
"""
import numpy as np
import matplotlib.pyplot as plt
from random import gauss
from functools import reduce
import pyvista as pv

from collections import deque

def get_radius (x,y,z):
    return np.sqrt(x**2+y**2+z**2)

class Sphere:
  def __init__(self, center=[0, 0, 0], radius=1.0):
    self._center = np.array(center)
    self._radius = radius

  def ray_inter(self, orig, dire):
    L = orig - self._center
    k1 = np.dot(dire, dire)
    k2 = 2*np.dot(L, dire)
    k3 = np.dot(L, L) - self._radius**2
    d = k2**2 - 4*k1*k3
    if d<0:
       return np.inf
    t1 = (-k2 + np.sqrt(d)) / (2*k1)
    t2 = (-k2 - np.sqrt(d)) / (2*k1)
    if t1>0 and t2>0:
       return min(t1, t2)
    return np.inf
    
def get_a_time(scene, angle_xy,angle_z):
    global ray_velocity, center
    direction = np.array([np.cos(angle_xy), np.sin(angle_xy), np.sin(angle_z)])
    r = []
    for o in scene:
       r.append(o.ray_inter(center, direction))
    return min(r)/ray_velocity if min(r)!=np.inf else np.inf

def interpolation (array_for_interpolation):
    inter_array = []
    for i in range(len(array_for_interpolation)):
        if i+1 == len(array_for_interpolation):
            break
        inter_array.append(np.linspace(array_for_interpolation[i],array_for_interpolation[i+1],3))
    return inter_array
    
sp1 = Sphere(center=[-1, -1, 1], radius=0.3)
sp2 = Sphere(center=[-1, 2, 2], radius=1)
sp3 = Sphere(center=[4, 5, 0], radius=0.1)
sp4 = Sphere(center=[1, 1, 1], radius=0.3)
sp5 = Sphere(center=[1, -1, 1], radius=0.3)
sp6 = Sphere(center=[0, -1, -1], radius=.2)
sphere_array = [sp1,sp2, sp5, sp4] #,sp2,sp3,sp4,sp5, sp6]

ray_velocity = .5;
center = np.array([0, 0, 0])
orig_vector = np.array([0, 0, 1])
angles = np.linspace(0, 2*np.pi, 180)
times = []
x, y, z = [], [], []
points = []
point_for_object=[]
step_for_ray= 60
for a_z in np.linspace(0, np.pi, step_for_ray):# было 90
    for a in np.linspace(0, 2*np.pi, step_for_ray*2): # было 180
        times.append(get_a_time(sphere_array, a, a_z))
        if times[-1]!= np.inf:
            x.append(np.cos(a)*times[-1]*ray_velocity)
            y.append(np.sin(a)*times[-1]*ray_velocity)
            z.append(np.sin(a_z)*times[-1]*ray_velocity)
            points.append([x[-1], y[-1], z[-1], np.dot(orig_vector, [x[-1], y[-1], z[-1]])])
            point_for_object.append([x[-1], y[-1], z[-1]])
        #print(f'x: {x[-1]}, y: {y[-1]}')

noise_mean = 0
noise_dev = .1
## добавление Шума к точкам
x = np.array(list(map(lambda t: t + gauss(noise_mean, noise_dev), x)))
y = np.array(list(map(lambda t: t + gauss(noise_mean, noise_dev), y)))
z = np.array(list(map(lambda t: t + gauss(noise_mean, noise_dev), z)))
# эйлеров критерий
euk_crit_max = 2
obj = []
array_obj = []
j=0

## Разделяем объекты
radius = np.array(list(map(lambda i,j,k: np.sqrt(i**2+j**2+k**2),x,y,z)))
coords = np.concatenate((x, y, z)).reshape((3, len(x)))
points.sort()
#print('coords: ' , points)
for i in range(len(radius)):
    if i+1 == len(radius):
        break
    if np.sqrt((coords[0][i+1]-coords[0][i])**2 +
            (coords[1][i+1]-coords[1][i])**2 +
            (coords[2][i+1]-coords[2][i])**2) >= euk_crit_max:
        array_obj.append(obj)
        obj= []
        j+=1
    coord = [x[i],y[i],z[i]]
    obj.append(coord)
array_obj.append(obj)
        
# Разделяем объекты через очереди
euk_crit_max=.9
array_obj= []
q = deque()
for i in point_for_object: # берем точку
    obj=[]
    point_for_object.remove(i)# удаляем из списка этот элемент (чтоб не было коллизий в следующем цикле)
    obj.append(i)
    object_border_1_point=[]
    for j in point_for_object:# сравниваем со всем остальными точками которые имеем
        if (np.sqrt((i[0]-j[0])**2+
            (i[1]-j[1])**2+
            (i[2]-j[2])**2) <= euk_crit_max): # якоже они близкие
            obj.append(j) # добавляем в лист с текущим объектом
            point_for_object.remove(j)# удаляем из всех точек этот элемент т.к.он уже принадлежит объекту
    object_border_1_point=obj.copy() # временый лист чтоб пройтись по всем точка еще по доп разу
    for k in object_border_1_point: # обработка по дельта окрестностями точки
        if (np.sqrt((j[0]-k[0])**2+
            (j[1]-k[1])**2+
            (j[2]-k[2])**2) <= euk_crit_max):
            obj.append(k)
           # point_for_object.remove(k)# удаляем из всех точек этот элемент т.к.он уже принадлежит объекту
           # идея релизнуть через рекурсию с заранее заданым шагом
    object_border_2_point=obj.copy()
    for l in object_border_2_point:
        for i_2 in point_for_object:
            if (np.sqrt((l[0]-i_2[0])**2+
                (l[1]-i_2[1])**2+
                (l[2]-i_2[2])**2) <= euk_crit_max): # якоже они близкие
                obj.append(i_2) # добавляем в лист с текущим объектом
                point_for_object.remove(i_2)# удаляем из всех точек этот элемент т.к.он уже принадлежит объекту
    array_obj.append(obj)
#print(coords [0][])
                         
print("Objects found: ", len(array_obj))
## начинаем инетрполировать
inter_x=[]
inter_y=[]
inter_z=[]
x_i=[]
y_i=[]
z_i=[]
for i in array_obj:
    for j in i:
        inter_x.append(j[0])
        inter_y.append(j[1])
        inter_z.append(j[2])
    inter_x=interpolation(inter_x)
    inter_y=interpolation(inter_y)
    inter_z=interpolation(inter_z)
    for k in inter_x:
        for l in k:
            x_i.append(l)
    for k in inter_y:
        for l in k:
            y_i.append(l)
    for k in inter_z:
          for l in k:
              z_i.append(l)       
    inter_x, inter_y, inter_z =[],[],[]

fig = plt.figure(figsize=(12, 12), dpi=100)
ax = fig.add_subplot(projection='3d')
ax.scatter(0, 0, 0, c='r', s=16)
ax.scatter(x, y, z)
# plt.xlim([-5, 5])
# plt.ylim([-5, 5])
plt.show()


fig = plt.figure(figsize=(12, 12), dpi=100)
ax = fig.add_subplot(projection='3d')
#plt.scatter(center[0], center[1], c='r', s=8)
ax.scatter(x_i, y_i, z_i)

x_object=[]
y_object=[]
z_object=[]
for i in array_obj[3]:
    x_object.append(i[0])
    y_object.append(i[1])
    z_object.append(i[2])

###Попытка сделать поверхность

points_for_delaunay_2d=[]
x_i, y_i, z_i = np.array(x_i), np.array(y_i),np.array(z_i)
points_for_delaunay_2d = np.c_[x_i.reshape(-1), y_i.reshape(-1), z_i.reshape(-1)]

cloud = pv.PolyData(points_for_delaunay_2d)
#cloud.plot(point_size=15)
surf = cloud.delaunay_2d()
surf.plot(show_edges=False)

fig = plt.figure(figsize=(12, 12), dpi=100)
ax = fig.add_subplot(projection='3d')
#plt.scatter(center[0], center[1], c='r', s=8)
ax.scatter(x_object, y_object, z_object)
# plt.xlim([-5, 5])
# plt.ylim([-5, 5])
#plt.show()
