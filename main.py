import pygame
from pygame.locals import *
import random
import math

import config
from planet import generation
from planet.planet import Planet
from planet.star import Star

from rendering.mesh import Mesh
from rendering.camera import Camera
from rendering.renderer import SceneRenderer

from debug.fps_counter import FPSCounter

def main():
    random.seed(config.WORLD_SEED)
    
    pygame.init()
    pygame.display.set_mode((config.WIDTH, config.HEIGHT), DOUBLEBUF | OPENGL)
    
    planets = []
    num_planets = random.randint(3, 6)
    
    for i in range(num_planets):
        orbit_distance = config.ORBIT_RADIUS + (i * 800.0)
        orbit_speed = random.uniform(0.0001, 0.0008) / (i + 1)
        spin_speed = random.uniform(0.1, 1.0)
        radius = config.PLANET_RADIUS * random.uniform(0.8, 1.5)
        
        planets.append(Planet(radius, orbit_distance, orbit_speed, spin_speed))
        
    middle_index = (len(planets) - 1) // 2
    default_target = planets[middle_index]
    
    random_temp = random.uniform(3000.0, 25000.0)
    random_size = random.uniform(15.0, 60.0)
    my_sun = Star(random_size, random_temp)
    
    star_data = generation.create_stars(config.STAR_COUNT)
    star_mesh = Mesh(star_data[0], colors=star_data[1], is_points=True)
    
    camera = Camera()
    camera.target = default_target 
    camera.min_zoom_exp = math.log(default_target.radius * 1.5) / math.log(1.2)
    camera.needs_alignment = True 
    
    renderer = SceneRenderer(initial_target=default_target)
    fps_ui = FPSCounter() 
    clock = pygame.time.Clock()

    while True:
        mouse_buttons = pygame.mouse.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    clicked_planet = renderer.planet_marker.get_clicked_planet(event.pos[0], event.pos[1])
                    clicked_sun = renderer.get_clicked_sun(event.pos[0], event.pos[1], my_sun)
                    
                    if clicked_planet and camera.target != clicked_planet:
                        camera.target = clicked_planet
                        camera.min_zoom_exp = math.log(clicked_planet.radius * 1.5) / math.log(1.2)
                        camera.max_zoom_exp = 32.0 
                        camera.target_zoom_exp = 12.0
                        camera.needs_alignment = True

                    elif clicked_sun and camera.target != clicked_sun:
                        camera.target = clicked_sun
                        camera.min_zoom_exp = math.log(clicked_sun.radius * 1.2) / math.log(1.2)
                        camera.max_zoom_exp = 55.0 
                        camera.target_pitch = 89.0
                        camera.target_yaw = 0.0
                        
                        max_orbit = max(p.orbit_radius for p in planets)
                        required_distance = max_orbit * 2.6
                        camera.target_zoom_exp = math.log(required_distance) / math.log(1.2)
                        camera.needs_alignment = False
                            
                if event.button == 4: 
                    camera.zoom(-0.75)
                if event.button == 5: 
                    camera.zoom(0.75)
                    
            if event.type == pygame.MOUSEMOTION and mouse_buttons[2]:
                camera.process_mouse_motion(event.rel[0], event.rel[1])

        for p in planets:
            p.update()
        my_sun.update()
        
        current_fps = clock.get_fps()
        camera.update(config.DEBUG_MODE, renderer.animations.transition_progress)

        if config.DEBUG_MODE:
            total_triangles = 0
            
            for p in planets:
                if p.active_lod_idx != -1:
                    active_mesh = p.lods[p.active_lod_idx][1]
                    if active_mesh.has_indices and not active_mesh.is_points:
                        total_triangles += active_mesh.index_count // 3
            
            fps_ui.draw(current_fps, total_triangles)
        
        renderer.render_frame(camera, star_mesh, my_sun, planets)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
