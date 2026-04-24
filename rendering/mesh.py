from OpenGL.GL import *
from OpenGL.arrays import vbo
import numpy as np

class Mesh:
    """Wraps OpenGL Vertex Buffer Objects (VBOs) for hardware-accelerated drawing."""
    def __init__(self, verts, colors=None, normals=None, indices=None, is_points=False):
        self.is_points = is_points
        self.vertex_count = len(verts)
        self.has_colors = colors is not None
        self.has_normals = normals is not None
        self.has_indices = indices is not None

        self.vbo_verts = vbo.VBO(verts)
        
        if self.has_colors:
            self.vbo_colors = vbo.VBO(colors)
            
        if self.has_normals:
            self.vbo_normals = vbo.VBO(normals)
            
        if self.has_indices:
            self.vbo_indices = vbo.VBO(indices, target=GL_ELEMENT_ARRAY_BUFFER)
            self.index_count = len(indices)

    def update_vertices(self, new_verts):
        """Dynamically updates the GPU Vertex Buffer Object (VBO) for geomorphing."""
        self.vbo_verts.bind()
        glBufferSubData(GL_ARRAY_BUFFER, 0, new_verts.nbytes, new_verts)
        self.vbo_verts.unbind()

    def draw(self):
        """Binds buffer arrays and invokes GPU drawing."""
        self.vbo_verts.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vbo_verts)

        if self.has_colors:
            self.vbo_colors.bind()
            glEnableClientState(GL_COLOR_ARRAY)
            glColorPointer(3, GL_FLOAT, 0, self.vbo_colors)

        if self.has_normals:
            self.vbo_normals.bind()
            glEnableClientState(GL_NORMAL_ARRAY)
            glNormalPointer(GL_FLOAT, 0, self.vbo_normals)

        if self.is_points:
            glDrawArrays(GL_POINTS, 0, self.vertex_count)
        else:
            self.vbo_indices.bind()
            glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)
            self.vbo_indices.unbind()

        if self.has_normals:
            self.vbo_normals.unbind()
            glDisableClientState(GL_NORMAL_ARRAY)
            
        if self.has_colors:
            self.vbo_colors.unbind()
            glDisableClientState(GL_COLOR_ARRAY)
            
        self.vbo_verts.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
