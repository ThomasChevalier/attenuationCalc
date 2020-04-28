from OpenGL import GL as gl
import numpy as np
import ctypes
import math


class Sphere:
    """
    Mesh of an uv sphere, based on http://www.songho.ca/opengl/gl_sphere.html#sphere

    Implements vertex coordinates, normals and texture coordinates.
    """
    def __init__(self, offset, segments, rings, radius):
        """
        Constructor.

        Args:
            offset: tuple (x, y, z) specifying the offset to apply on each vertex coordinates.
            segments: the number of meridians
            rings: the number of parallels. Usually half the number of segments.
            radius:  the radius of the sphere.
        """

        self.offset_x, self.offset_y, self.offset_z = offset
        self.segments = segments
        self.rings = rings
        self.radius = radius

        self.vertices = []
        self.normals  = []
        self.textures = []
        self.indices  = []

        self._buildMesh()
        self._sendToGPU()

    def _buildMesh(self):
        segmentStep = 2*math.pi/self.segments
        ringStep = math.pi/self.rings

        for i in range(0, self.rings+1):
            u = math.pi/2-i*ringStep
            y = self.radius * math.sin(u)  # z

            for j in range(0, self.segments+1):
                v = j * segmentStep
                z = self.radius * math.cos(u) * math.cos(v)  # x
                x = self.radius * math.cos(u) * math.sin(v)  # y

                self.vertices.extend([x+self.offset_x, y+self.offset_y, z+self.offset_z])
                self.normals.extend([c/self.radius for c in [x, y, z]])
                self.textures.extend([j/self.segments, i/self.rings])

        #  indices
        #  k1--k1+1
        #  |  / |
        #  | /  |
        #  k2--k2+1

        for i in range(0, self.rings):
            k1 = i * (self.segments+1)
            k2 = k1+self.segments+1
            for j in range(0, self.segments):
                if i != 0:
                    self.indices.extend([k1, k2, k1+1])
                if i != self.rings-1:
                    self.indices.extend([k1+1, k2, k2+1])
                k1, k2 = k1+1, k2+1

    def _sendToGPU(self):
        interleavedData = []
        count = len(self.vertices)/3

        if not math.isclose(count, round(count)):
            raise RuntimeError("Number of vertices is not a multiple of 3 : {} != {}.".format(count, round(count)))
        count = round(count)
        for i in range(count):
            interleavedData.extend(self.vertices[i*3:(i+1)*3])
            interleavedData.extend(self.normals[i*3:(i+1)*3])
            interleavedData.extend(self.textures[i*2:(i+1)*2])

        self.VAO = gl.glGenVertexArrays(1)
        self.VBO = gl.glGenBuffers(1)
        self.EBO = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.VAO)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, np.array(interleavedData, dtype='float32'), gl.GL_STATIC_DRAW)

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, np.array(self.indices, dtype='uint32'), gl.GL_STATIC_DRAW)

        stride = 8*4
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, stride, ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)

        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, False, stride, ctypes.c_void_p(3*4))
        gl.glEnableVertexAttribArray(1)

        gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, False, stride, ctypes.c_void_p(6*4))
        gl.glEnableVertexAttribArray(2)

        gl.glBindVertexArray(0)

    def draw(self):
        """
        Draw the mesh
        """
        gl.glBindVertexArray(self.VAO)
        gl.glDrawElements(gl.GL_TRIANGLES, len(self.indices), gl.GL_UNSIGNED_INT, None)

    def drawInstanced(self, number):
        gl.glBindVertexArray(self.VAO)
        gl.glDrawElementsInstanced(gl.GL_TRIANGLES, len(self.indices), gl.GL_UNSIGNED_INT, None, number)
