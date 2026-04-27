import math
import random
import numpy as np
import vnoise

from planet.star import Star

def get_terrain_color(height):
    """Maps 3D noise height to terrain color bands."""
    if height < -0.15: return (0.05, 0.1, 0.4) 
    if height < 0.0: return (0.1, 0.3, 0.7) 
    if height < 0.08: return (0.95, 0.9, 0.7) 
    if height < 0.4: return (0.1, 0.5, 0.1) 
    if height < 0.7: return (0.4, 0.4, 0.4)
    return (1.0, 1.0, 1.0)                   

def kelvin_to_rgb(temperature):
    """Approximates star color based on Kelvin using black-body math."""
    temp = max(1000.0, min(temperature, 40000.0)) / 100.0

    if temp <= 66:
        r = 255.0
    else:
        r = temp - 60.0
        r = 329.698727446 * (r ** -0.1332047592)

    if temp <= 66:
        g = temp
        g = 99.4708025861 * math.log(g) - 161.1195681661
    else:
        g = temp - 60.0
        g = 288.1221695283 * (g ** -0.0755148492)

    if temp >= 66:
        b = 255.0
    elif temp <= 19:
        b = 0.0
    else:
        b = temp - 10.0
        b = 138.5177312231 * math.log(b) - 305.0447927307

    r = max(0.0, min(255.0, r)) / 255.0
    g = max(0.0, min(255.0, g)) / 255.0
    b = max(0.0, min(255.0, b)) / 255.0

    return (r, g, b)

def create_sphere(radius, subdivisions, noise_enabled=True, base_color=(1.0, 1.0, 1.0), noise_gen=None, prev_subdivisions=None):
    """Generates a 3D procedural sphere mesh with true geomorphing animation data."""
    vn = noise_gen if noise_gen else vnoise.Noise()
    vertices, low_detail_verts, colors, normals = [], [], [], []
    
    if prev_subdivisions is None:
        prev_subdivisions = subdivisions
        
    for i in range(subdivisions + 1):
        lat = math.pi * i / subdivisions
        
        low_lat_step = math.pi / prev_subdivisions
        low_lat = round(lat / low_lat_step) * low_lat_step
        
        for j in range(subdivisions + 1):
            lon = 2 * math.pi * j / subdivisions
            
            low_lon_step = (2 * math.pi) / prev_subdivisions
            low_lon = round(lon / low_lon_step) * low_lon_step
            
            x, y, z = math.sin(lat) * math.cos(lon), math.cos(lat), math.sin(lat) * math.sin(lon)
            lx, ly, lz = math.sin(low_lat) * math.cos(low_lon), math.cos(low_lat), math.sin(low_lat) * math.sin(low_lon)
            
            if noise_enabled:
                h = vn.noise3(x * 2.5, y * 2.5, z * 2.5)
                colors.append(get_terrain_color(h))
                displacement = 1.0 + (h * 0.15) 
                vertices.append([x * radius * displacement, y * radius * displacement, z * radius * displacement])
                
                low_h = vn.noise3(lx * 2.5, ly * 2.5, lz * 2.5)
                low_displacement = 1.0 + (low_h * 0.15)
                
                low_detail_verts.append([x * radius * low_displacement, y * radius * low_displacement, z * radius * low_displacement])
            else:
                colors.append(base_color) 
                vertices.append([x * radius, y * radius, z * radius])
                low_detail_verts.append([x * radius, y * radius, z * radius])
                
            normals.append([x, y, z])
            
    indices = []
    for i in range(subdivisions):
        for j in range(subdivisions):
            first = (i * (subdivisions + 1)) + j
            second = first + subdivisions + 1
            indices.extend([first, second, first + 1, second, second + 1, first + 1])
            
    return (np.array(vertices, dtype='float32'), np.array(colors, dtype='float32'), 
            np.array(normals, dtype='float32'), np.array(indices, dtype='uint32'),
            np.array(low_detail_verts, dtype='float32'))

import random
import math

def create_stars(star_count):
    stars = []
    for i in range(star_count):
        theta = random.uniform(0, 2 * math.pi)
        phi = math.acos(random.uniform(-1, 1))
        
        r = random.uniform(50000.0, 500000.0) 
        
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)

        temperature = random.uniform(3000.0, 25000.0)
        
        new_star = Star(radius=random.uniform(5.0, 20.0), temperature=temperature, subdivisions=30, is_background=True)
        new_star.name = f"BackgroundStar_{i}"
        
        new_star.px = x
        new_star.py = y
        new_star.pz = z
        stars.append(new_star)
        
    return stars