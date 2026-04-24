import pygame
import math
from OpenGL.GL import *
from OpenGL.GLU import *
import config

class PlanetMarker:
    """Draws a 2D UI overlay and label for distant planets."""
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont('Consolas', 11, bold=False)
        self.circle_radius = 4.0 
        self.active_markers = {}

    def draw(self, planet, camera, alpha):
        if alpha <= 0.01:
            if planet in self.active_markers:
                del self.active_markers[planet]
            return

        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        win_x, win_y, win_z = gluProject(planet.px, 0.0, planet.pz, modelview, projection, viewport)

        if 0.0 < win_z < 1.0:
            win_x, win_y = round(win_x), round(win_y)
            self.active_markers[planet] = (win_x, win_y)

            text_surface = self.font.render(planet.name, True, (200, 200, 200))
            # Fix: Apply the animated alpha to the text surface
            text_surface.set_alpha(int(alpha * 255))
            text_data = pygame.image.tostring(text_surface, "RGBA", True)
            w, h = text_surface.get_size()

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
            
            glEnable(GL_POINT_SMOOTH)
            glPointSize(self.circle_radius * 2)
            glBegin(GL_POINTS)
            
            glColor4f(*planet.marker_color, alpha)
            glVertex2f(win_x, win_y)
            glEnd()
            glPointSize(1.0)
            glDisable(GL_POINT_SMOOTH)
            
            glRasterPos2i(int(win_x + self.circle_radius + 6), int(win_y - (h / 2)))
            glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

            glDisable(GL_BLEND)
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix()
        else:
            if planet in self.active_markers:
                del self.active_markers[planet]

    def get_clicked_planet(self, mouse_x, mouse_y):
        gl_mouse_y = config.HEIGHT - mouse_y
        for planet, (px, py) in self.active_markers.items():
            dist = math.hypot(px - mouse_x, py - gl_mouse_y)
            if dist <= self.circle_radius + 6.0:
                return planet
        return None
