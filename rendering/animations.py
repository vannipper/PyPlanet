import math

class Animations:
    """Manages smooth interpolation math for camera movements and UI fading."""
    def __init__(self):
        self.focus_x = 0.0
        self.focus_z = 0.0
        self.marker_alphas = {}
        
        self.transition_progress = 1.0
        self.source_x = 0.0
        self.source_z = 0.0
        self.current_target = None

    def update(self, target, planets, zoom_distance, debug_mode):
        if target != self.current_target:
            self.source_x = self.focus_x
            self.source_z = self.focus_z
            self.current_target = target
            self.transition_progress = 0.0

        target_x = target.px if target else 0.0
        target_z = target.pz if target else 0.0

        if debug_mode:
            self.transition_progress = 1.0
            self.focus_x = target_x
            self.focus_z = target_z
        else:
            if self.transition_progress < 1.0:
                self.transition_progress += 0.015 
                if self.transition_progress > 1.0:
                    self.transition_progress = 1.0

            t = self.transition_progress
            ease = t * t * (3 - 2 * t)

            self.focus_x = self.source_x + (target_x - self.source_x) * ease
            self.focus_z = self.source_z + (target_z - self.source_z) * ease

        for planet in planets:
            if planet not in self.marker_alphas:
                self.marker_alphas[planet] = 0.0

            dist_to_focus = math.hypot(planet.px - self.focus_x, planet.pz - self.focus_z)
            actual_distance = math.hypot(dist_to_focus, zoom_distance)

            target_alpha = 1.0 if actual_distance >= 150.0 else 0.0
            self.marker_alphas[planet] += (target_alpha - self.marker_alphas[planet]) * 0.1
            self.marker_alphas[planet] = max(0.0, min(1.0, self.marker_alphas[planet]))