from OpenGL import GL as gl
from PIL import Image
import PIL
import numpy as np


class Texture:
    def __init__(self, filename, unit, flip=False):
        # Create texture
        self.ID = gl.glGenTextures(1)
        self.unit = unit

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.ID)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        if flip:
            im = Image.open(filename).transpose(PIL.Image.FLIP_TOP_BOTTOM)
        else:
            im = Image.open(filename)
        data = np.array(im)

        rgbType = gl.GL_RGB if data.shape[2] == 3 else gl.GL_RGBA

        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, rgbType, im.width, im.height, 0, rgbType, gl.GL_UNSIGNED_BYTE, data)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    def bind(self):
        gl.glActiveTexture(gl.GL_TEXTURE0+self.unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.ID)
