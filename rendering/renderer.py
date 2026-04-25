from OpenGL.GL import *
from OpenGL.GLU import *
import math
import config
from debug.pole_visualizer import PoleVisualizer
from ui.planet_marker import PlanetMarker
from ui.orbit_visualizer import OrbitVisualizer
from rendering.animations import Animations

class SceneRenderer:
    def __init__(self, initial_target=None):
        self.init_lighting()
        self.pole_viz = PoleVisualizer()
        self.planet_marker = PlanetMarker()
        self.orbit_viz = OrbitVisualizer()
        self.animations = Animations()
        self.sun_screen_pos = None
        self.sun_screen_radius = 0
        
        if initial_target:
            self.animations.focus_x = initial_target.px
            self.animations.focus_y = getattr(initial_target, 'py', 0.0)
            self.animations.focus_z = initial_target.pz

    def init_lighting(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.02, 0.02, 0.05, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.9, 1.0])
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CW)

    def render_frame(self, camera, stars, sun, planets):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        zoom_dist = abs(camera.get_zoom_level())
        self.animations.update(camera.target, planets, zoom_dist, config.DEBUG_MODE)
        
        if config.DEBUG_MODE:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        gluPerspective(45, (config.WIDTH / config.HEIGHT), 1.0, 1000000.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_LIGHTING)

        focus_x = self.animations.focus_x
        focus_y = getattr(self.animations, 'focus_y', 0.0)
        focus_z = self.animations.focus_z

        glTranslatef(0, 0, camera.get_zoom_level())
        glRotatef(camera.pitch, 1, 0, 0)
        glRotatef(camera.yaw, 0, 1, 0)
        glTranslatef(-focus_x, -focus_y, -focus_z)

        RENDER_THRESHOLD = 8000.0 
        
        glDisable(GL_DEPTH_TEST)
        glPointSize(1.5)
        glBegin(GL_POINTS)
        for star in stars:
            dx = star.px - focus_x
            dy = star.py - focus_y
            dz = star.pz - focus_z
            dist = math.sqrt(dx**2 + dy**2 + dz**2)

            if dist > RENDER_THRESHOLD:
                glColor3fv(star.marker_color)
                glVertex3f(star.px, star.py, star.pz)
        glEnd()

        glEnable(GL_DEPTH_TEST)
        
        for star in stars:
            dx = star.px - focus_x
            dy = star.py - focus_y
            dz = star.pz - focus_z
            dist = math.sqrt(dx**2 + dy**2 + dz**2)

            if dist <= RENDER_THRESHOLD:
                glColor3fv(star.marker_color)
                glPushMatrix()
                glTranslatef(star.px, star.py, star.pz)
                star.draw(camera)
                glPopMatrix()

        self.orbit_viz.draw(planets, self.animations.marker_alphas)

        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        win_x, win_y, win_z = gluProject(sun.px, sun.py, sun.pz, modelview, projection, viewport)
        edge_x, edge_y, _ = gluProject(sun.px + sun.radius, sun.py, sun.pz, modelview, projection, viewport)
        
        if 0.0 < win_z < 1.0:
            self.sun_screen_pos = (win_x, win_y)
            self.sun_screen_radius = math.hypot(edge_x - win_x, edge_y - win_y)
        else:
            self.sun_screen_pos = None

        glDisable(GL_LIGHTING)
        glPushMatrix()
        glTranslatef(sun.px, 0, sun.pz)
        glPushMatrix()
        glRotatef(sun.axial_tilt, 1, 0, 0) 
        glRotatef(sun.spin, 0, 1, 0) 
        sun.draw(camera)
        glPopMatrix()
        glPopMatrix()

        glEnable(GL_LIGHTING)
        glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 0, 1])

        for planet in planets:
            glPushMatrix()
            glTranslatef(planet.px, 0, planet.pz)
            glPushMatrix()
            glRotatef(planet.axial_tilt, 1, 0, 0) 
            glRotatef(planet.spin, 0, 1, 0) 
            planet.draw(camera) 
            glPopMatrix()
            if config.DEBUG_MODE:
                self.pole_viz.draw(planet, camera)
            glPopMatrix()
        
        for planet in planets:
            alpha = self.animations.marker_alphas.get(planet, 0.0)
            self.planet_marker.draw(planet, camera, alpha)

    def get_clicked_sun(self, mouse_x, mouse_y, sun):
        if self.sun_screen_pos:
            gl_mouse_y = config.HEIGHT - mouse_y
            dist = math.hypot(self.sun_screen_pos[0] - mouse_x, self.sun_screen_pos[1] - gl_mouse_y)
            expanded_radius = self.sun_screen_radius * 1.2
            if dist <= expanded_radius:
                return sun
        return None

    def get_clicked_star(self, mouse_x, mouse_y, stars):
        """Projects 3D stars to 2D screen space to detect clicks (DEBUG ONLY)."""
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        gl_mouse_y = config.HEIGHT - mouse_y
        
        closest_star = None
        min_dist = 10.0
        
        for star in stars:
            win_x, win_y, win_z = gluProject(star.px, star.py, star.pz, modelview, projection, viewport)
            
            if 0.0 < win_z < 1.0:
                dist = math.hypot(win_x - mouse_x, win_y - gl_mouse_y)
                if dist < min_dist:
                    min_dist = dist
                    closest_star = star
                    
        return closest_star
