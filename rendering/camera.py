import math

class Camera:
    def __init__(self):
        self.zoom_exp = 12.0
        self.target_zoom_exp = 12.0
        self.min_zoom_exp = 6.0
        self.max_zoom_exp = 32.0 
        self.yaw = 0.0
        self.target_yaw = 0.0
        self.pitch = 0.0
        self.target_pitch = 0.0
        self.target = None 
        self.needs_alignment = False

    def process_mouse_motion(self, rel_x, rel_y):
        self.target_yaw += rel_x * 0.225
        self.target_pitch += rel_y * 0.225
        self.target_pitch = max(-89.0, min(89.0, self.target_pitch))

    def zoom(self, amount):
        self.target_zoom_exp = max(self.min_zoom_exp, min(self.max_zoom_exp, self.target_zoom_exp + amount))

    def update(self, debug_mode, transition_progress):
        if self.needs_alignment and transition_progress > 0.8:
            ideal_yaw = math.degrees(math.atan2(self.target.px, -self.target.pz))
            diff = (ideal_yaw - self.target_yaw) % 360
            if diff > 180:
                diff -= 360
            self.target_yaw += diff
            self.target_pitch = 0.0
            self.needs_alignment = False

        if debug_mode:
            self.zoom_exp = self.target_zoom_exp
            self.yaw = self.target_yaw
            self.pitch = self.target_pitch
        else:
            self.zoom_exp += (self.target_zoom_exp - self.zoom_exp) * 0.05
            self.yaw += (self.target_yaw - self.yaw) * 0.05
            self.pitch += (self.target_pitch - self.pitch) * 0.05

    def get_zoom_level(self):
        return -(1.2 ** self.zoom_exp)