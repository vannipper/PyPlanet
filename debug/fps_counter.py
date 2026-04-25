import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import config

class FPSCounter:
    """Projects standard 2D Pygame text over the 3D OpenGL context."""
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont('Consolas', 18, bold=True)
        self.display_fps = 0.0
        self.display_tris = 0
        self.display_zoom = 0.0
        self.frames_passed = 0

    def draw(self, current_fps, current_tris, current_zoom):
        """Calculates smoothed framerate and renders it via orthographic projection."""
        self.frames_passed += 1
        
        if self.frames_passed >= 10:
            self.display_fps = current_fps
            self.display_tris = current_tris
            self.display_zoom = current_zoom
            self.frames_passed = 0

        text_str_1 = f"FPS: {self.display_fps:.1f} | Tris: {self.display_tris:,}"
        text_str_2 = f"Zoom: {self.display_zoom:.2f}"
        
        text_surface_1 = self.font.render(text_str_1, True, (0, 255, 0)) 
        text_data_1 = pygame.image.tostring(text_surface_1, "RGBA", True)
        width_1, height_1 = text_surface_1.get_size()

        text_surface_2 = self.font.render(text_str_2, True, (0, 255, 0)) 
        text_data_2 = pygame.image.tostring(text_surface_2, "RGBA", True)
        width_2, height_2 = text_surface_2.get_size()

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, config.WIDTH, 0, config.HEIGHT)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL) 

        glRasterPos2i(10, config.HEIGHT - 25)
        glDrawPixels(width_1, height_1, GL_RGBA, GL_UNSIGNED_BYTE, text_data_1)

        glRasterPos2i(10, config.HEIGHT - 45)
        glDrawPixels(width_2, height_2, GL_RGBA, GL_UNSIGNED_BYTE, text_data_2)

        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()