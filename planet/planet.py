import math
import random
import vnoise
import numpy as np
import multiprocessing as mp
import queue
import collections

from planet import generation
from rendering.mesh import Mesh

def _background_loader_process(radius, seed, data_queue):
    noise_gen = vnoise.Noise(seed)
    
    min_zoom_exp = math.log(radius * 1.5) / math.log(1.2)
    max_zoom_exp = 32.0  
    
    min_subs = 60     
    max_subs = 250    
    
    min_dist = 1.2 ** min_zoom_exp
    max_dist = 1.2 ** max_zoom_exp
    
    surf_min = max(0.1, min_dist - radius)
    surf_max = max(0.1, max_dist - radius)
    
    inv_min = 1.0 / surf_min
    inv_max = 1.0 / surf_max
    
    current_exp = max_zoom_exp
    
    while current_exp >= min_zoom_exp:
        current_dist = 1.2 ** current_exp
        current_surf = max(0.1, current_dist - radius)
        inv_current = 1.0 / current_surf
        
        t = (inv_current - inv_max) / (inv_min - inv_max)
        t = max(0.0, min(1.0, t))
        
        current_subs = int(min_subs + (t * (max_subs - min_subs)))
        prev_subs = int(current_subs * 0.8)
        
        p_data = generation.create_sphere(
            radius, 
            current_subs, 
            noise_enabled=True, 
            noise_gen=noise_gen, 
            prev_subdivisions=prev_subs
        ) 
        
        data_queue.put((current_dist, p_data))
        
        current_exp -= 1.0

    if (current_exp + 1.0) > min_zoom_exp:
        final_dist = 1.2 ** min_zoom_exp
        final_prev = int(max_subs * 0.8)
        
        p_data_final = generation.create_sphere(
            radius, 
            max_subs, 
            noise_enabled=True, 
            noise_gen=noise_gen, 
            prev_subdivisions=final_prev
        )
        data_queue.put((final_dist, p_data_final))

class Planet:
    """Encapsulates geometry, asynchronous LODs, Geomorphing, and orbital mechanics."""
    def __init__(self, radius, orbit_radius, orbit_speed=0.0005, spin_speed=0.5):
        self.radius = radius
        
        self.seed = random.randint(0, 999999)
        self.noise_gen = vnoise.Noise(self.seed)
        
        # --- Metadata Generation ---
        prefixes = ["Kepler", "Gliese", "Zeta", "Nova", "Aero", "Vex", "Kryto", "Terra", "Helios"]
        suffixes = ["Prime", "Major", "Minor", "X", "V", "B"]
        self.name = f"{random.choice(prefixes)} {random.choice(suffixes)}-{random.randint(10, 99)}"
        
        base_p_data = generation.create_sphere(self.radius, 30, noise_enabled=True, noise_gen=self.noise_gen, prev_subdivisions=30)
        
        color_tuples = [tuple(c) for c in base_p_data[1]]
        self.marker_color = collections.Counter(color_tuples).most_common(1)[0][0]
        
        # Array format: (max_distance, Mesh_Object, blocky_low_detail_vertices, fully_displaced_vertices)
        self.lods = [
            (35.0, Mesh(base_p_data[0], base_p_data[1], base_p_data[2], base_p_data[3]), base_p_data[4], base_p_data[0]),        
            (float('inf'), Mesh(base_p_data[0], base_p_data[1], base_p_data[2], base_p_data[3]), base_p_data[4], base_p_data[0]) 
        ]
        
        self.active_lod_idx = -1
        self.transition_progress = 1.0
        
        self.mesh_queue = mp.Queue()
        self.loader_process = mp.Process(
            target=_background_loader_process, 
            args=(self.radius, self.seed, self.mesh_queue),
            daemon=True
        )
        self.loader_process.start()
        
        self.orbit_radius = orbit_radius
        self.orbit_speed = orbit_speed
        self.orbit_vertices = self._generate_orbit_path()
        self.spin_speed = spin_speed
        
        self.spin = 0.0
        self.orbit_angle = 0.0
        self.px = 0.0
        self.py = 0.0
        self.pz = 0.0
        self.axial_tilt = random.triangular(0, 90, 15)

    def _generate_mesh(self, subdivisions, prev_subdivisions):
        """Helper function to build a mesh and extract geomorphing animation states."""
        p_data = generation.create_sphere(self.radius, subdivisions, noise_enabled=True, noise_gen=self.noise_gen, prev_subdivisions=prev_subdivisions) 
        mesh = Mesh(p_data[0], p_data[1], p_data[2], p_data[3])
        return mesh, p_data[4], p_data[0]

    def _generate_orbit_path(self):
        segments = 128
        vertices = []
        for i in range(segments + 1):
            angle = (i / segments) * 2.0 * math.pi
            vertices.append([math.cos(angle) * self.orbit_radius, 0, math.sin(angle) * self.orbit_radius])
        return np.array(vertices, dtype='float32')

    def update(self):
        """Advances the planet's orbital mechanics by one frame."""
        self.spin += self.spin_speed
        self.orbit_angle += self.orbit_speed
        self.px = math.cos(self.orbit_angle) * self.orbit_radius
        self.pz = math.sin(self.orbit_angle) * self.orbit_radius
        
        try:
            while True:
                max_dist, p_data = self.mesh_queue.get_nowait()
                new_mesh = Mesh(p_data[0], p_data[1], p_data[2], p_data[3])
                self.lods.append((max_dist, new_mesh, p_data[4], p_data[0]))
                self.lods.sort(key=lambda x: x[0])
        except queue.Empty:
            pass
        
    def draw(self, camera):
        """Selects and renders the appropriate LOD mesh, blending vertices on transition."""
        distance = abs(camera.get_zoom_level())
        
        target_idx = len(self.lods) - 1
        for i, (max_dist, *_) in enumerate(self.lods):
            if distance <= max_dist:
                target_idx = i
                break
                
        if target_idx != self.active_lod_idx:
            self.active_lod_idx = target_idx
            self.transition_progress = 0.0
            
        active_mesh, low_detail_verts, target_verts = self.lods[self.active_lod_idx][1:4]
        
        if self.transition_progress < 1.0:
            self.transition_progress += 0.05 
            if self.transition_progress > 1.0:
                self.transition_progress = 1.0

            current_verts = low_detail_verts + ((target_verts - low_detail_verts) * self.transition_progress)
            
            current_verts = np.ascontiguousarray(current_verts, dtype=np.float32)
            active_mesh.update_vertices(current_verts)

        active_mesh.draw()
