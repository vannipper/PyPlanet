import pygame
import math
from OpenGL.GL import *
from OpenGL.GLU import *
import config

class PoleVisualizer:
    """
    A diagnostic tool for visualizing planetary poles and axial tilt.
    Renders absolute global vertical limits alongside the planet's localized rotational axis.
    """
    def __init__(self):
        self.length = 2.5
        self.max_distance = 250.0 
        
        pygame.font.init()
        self.font = pygame.font.SysFont('Consolas', 14, bold=True)

    def draw(self, planet, camera):
        """
        Renders the pole lines and tilt arc if the camera is within the maximum viewing distance.
        """
        current_distance = abs(camera.get_zoom_level())
        
        if current_distance > self.max_distance:
            return

        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glLineWidth(1.0) 

        glBegin(GL_LINES)
        glColor3f(1.0, 0.0, 0.0) 
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, self.length, 0.0) 
        
        glColor3f(0.0, 0.0, 1.0) 
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, -self.length, 0.0) 
        glEnd()

        glPushMatrix()
        glRotatef(planet.axial_tilt, 1, 0, 0)
        
        glBegin(GL_LINES)
        glColor3f(1.0, 0.0, 0.0) 
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, self.length, 0.0) 
        
        glColor3f(0.0, 0.0, 1.0) 
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, -self.length, 0.0) 
        glEnd()
        glPopMatrix()

        tilt_deg = planet.axial_tilt
        tilt_rad = math.radians(tilt_deg)
        
        glColor3f(1.0, 1.0, 0.0)
        glBegin(GL_LINE_STRIP)
        
        segments = max(5, int(tilt_deg / 5)) 
        for i in range(segments + 1):
            t = (i / segments) * tilt_rad
            y = self.length * math.cos(t)
            z = self.length * math.sin(t)
            glVertex3f(0.0, y, z)
        glEnd()

        mid_t = tilt_rad / 2.0
        mid_x = 0.0
        mid_y = self.length * math.cos(mid_t)
        mid_z = self.length * math.sin(mid_t)

        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        win_x, win_y, win_z = gluProject(mid_x, mid_y, mid_z, modelview, projection, viewport)

        if 0.0 < win_z < 1.0:
            text_str = f"{tilt_deg:.1f}°"
            text_surface = self.font.render(text_str, True, (255, 255, 0)) 
            text_data = pygame.image.tostring(text_surface, "RGBA", True)
            w, h = text_surface.get_size()

            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            gluOrtho2D(0, config.WIDTH, 0, config.HEIGHT)

            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()

            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL) 

            glRasterPos2i(int(win_x) + 10, int(win_y))
            glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

            glDisable(GL_BLEND)
            if config.DEBUG_MODE:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
