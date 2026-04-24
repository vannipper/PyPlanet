import math
from OpenGL.GL import *

class OrbitVisualizer:
    """Renders fading orbital paths that trail behind moving celestial bodies."""
    
    def __init__(self):
        # Defines the visible length of the tail (one-third of a full orbit)
        self.trail_length = (2.0 * math.pi) / 3.0
        self.segments = 60

    def draw(self, planets, marker_alphas):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_LIGHTING)
        glLineWidth(1.5)

        for planet in planets:
            if not hasattr(planet, 'orbit_radius') or planet.orbit_radius <= 0.0:
                continue

            alpha_multiplier = marker_alphas.get(planet, 0.0)
            if alpha_multiplier <= 0.0:
                continue

            r, g, b = planet.dominant_color if hasattr(planet, 'dominant_color') else (1.0, 1.0, 1.0)

            glBegin(GL_LINE_STRIP)

            for i in range(self.segments + 1):
                progress = i / self.segments

                angle = planet.orbit_angle - (self.trail_length * progress)

                x = math.cos(angle) * planet.orbit_radius
                z = math.sin(angle) * planet.orbit_radius

                current_alpha = alpha_multiplier * (1.0 - progress)

                glColor4f(r, g, b, current_alpha)
                glVertex3f(x, 0.0, z)

            glEnd()

        glEnable(GL_LIGHTING)
        glDisable(GL_BLEND)