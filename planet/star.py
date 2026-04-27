import queue

from planet.planet import Planet
from planet import generation
from rendering.mesh import Mesh

class Star(Planet):
    def __init__(self, radius, temperature, subdivisions=60, is_background=False):
        self.radius = radius
        self.orbit_radius = 0.0
        self.orbit_speed = 0.0
        self.spin_speed = 0.01
        self.spin = 0.0
        self.orbit_angle = 0.0
        
        self.px = 0.0
        self.py = 0.0
        self.pz = 0.0
        self.axial_tilt = 0.0
        
        self.name = "Sun"
        self.temperature = temperature
        self.marker_color = generation.kelvin_to_rgb(temperature)
        
        self.subdivisions = subdivisions
        self.is_background = is_background
        
        self.lods = []
        self.active_lod_idx = -1
        self.transition_progress = 1.0
        self.orbit_vertices = []
        
        self.mesh_queue = queue.Queue() 

        if not is_background:
            self.generate_mesh()

    def generate_mesh(self):
        """Builds the 3D geometry when the camera gets close."""
        if not self.lods:
            s_data = generation.create_sphere(self.radius, self.subdivisions, noise_enabled=False, base_color=self.marker_color)
            mesh = Mesh(s_data[0], s_data[1], s_data[2], s_data[3])
            self.lods = [(float('inf'), mesh, s_data[4], s_data[0])]
            self.active_lod_idx = 0

    def offload_mesh(self):
        """Destroys the 3D geometry to free up memory when far away."""
        if self.lods:
            self.lods = []
            self.active_lod_idx = -1