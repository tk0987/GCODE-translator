"""

︻╦̵̵̿╤── GCODE_KILLER ╾━╤デ╦︻

This is an example how to convert gcode to cartesian coordinates - including archs (here cw only).
For ccw archs you will need to increment angle - not decrement like here.

The purpose of creating this 'translator code' was the use in my cnc multitool.

"""


import numpy as np
import re
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def arch_cw(x_prev, y_prev, i, j, x, y):
    radius = 0.0
    angle_arch = 0.0

    try:
        if i == 0.0 and j == 0.0:
            angle_arch = 0.0
        else:
            radius = np.sqrt(i**2 + j**2)
            ai_denominator = (y_prev - j)
            axy_denominator = (x_prev + i - x)
            
            if abs(ai_denominator) < 1e-6 or abs(axy_denominator) < 1e-6:
                ai = 0.0
                axy = 0.0
            else:
                ai = (x_prev - i) / ai_denominator
                axy = (y_prev + j - y) / axy_denominator
            
            if (1 + ai * axy) < 1e-6:
                angle_arch = 0.0
            else:
                angle_arch = np.arctan(abs(ai - axy) / (1 + ai * axy))
                
            if x == x_prev and y == y_prev:
                angle_arch = 2 * np.pi
            if x < x_prev or y < y_prev:
                angle_arch = 2 * np.pi - angle_arch

        decrement = 0.01
        arc_points = []
        while angle_arch >= 0.0:
            angle_arch -= decrement
            x_arc = i + radius * np.cos(angle_arch)
            y_arc = j + radius * np.sin(angle_arch)
            arc_points.append((x_arc, y_arc))

        return arc_points
    except Exception as e:
        print(f"Error in arch_cw: {e}")
        return []

f = open("demo.gcode", "r", encoding='utf-8')
lines = [line for line in f]
temp = []
index = 0
z = 0.0
x = 0.0
y = 0.0
x_prev = 0.0
y_prev = 0.0
z_prev = 0.0

for line2 in lines:
    try:
        x_prev = x
        y_prev = y
        z_prev = z
        i = 0.0
        j = 0.0
        feed_rate = 1.0
        k = 0.0
        g = 0.0
        parts = re.findall(r'([A-Z]+)([+-]?\d+(?:\.\d+)?)', line2)
        for part in parts:
            code, value = part
            value = float(value)
            if code == 'X':
                x = value
            if code == 'Y':
                y = value
            if code == 'Z':
                z = value
            if code == 'I':
                i = value
            if code == 'J':
                j = value
            if code == 'K':
                k = value
            if code == 'F':
                feed_rate = value
            if code == 'G':
                g = value
            
        if i != 0.0 or j != 0.0:
            arc_points = arch_cw(x_prev, y_prev, i, j, x, y)
            for point in arc_points:
                x1, y1 = point
                x1 = x_prev + x1
                y1 = y_prev + y1
                temp.append([x1, y1, z])
        else:
            temp.append([x, y, z])
        
        index += 1

    except Exception as e:
        print(f"Error parsing line: {line2}")
        print(f"Error message: {e}")

temp_array = np.array(temp)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
x, y, z = temp_array.T
ax.plot(x, y, z, c='r', linestyle='-', label='Lines', linewidth=0.07)
ax.set_xlabel('X-axis')
ax.set_ylabel('Y-axis')
ax.set_zlabel('Z-axis')
ax.legend()
plt.show()
