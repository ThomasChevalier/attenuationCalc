from OpenGL import GL as gl
import glm


class Shaders:
    def __init__(self, vertexShaderFile, fragmentShaderFile):
        self.vertexShader = ""
        self.vertexID = 0

        self.fragmentShader = ""
        self.fragmentID = 0

        self.shaderProgram = 0
        self.cachedLocation = {}

        self.load(vertexShaderFile, fragmentShaderFile)
        self.link()

    def load(self, vertexShaderFile, fragmentShaderFile):
        self.vertexShader, self.vertexID = self._loadAndCompile(vertexShaderFile, gl.GL_VERTEX_SHADER)
        self.fragmentShader, self.fragmentID = self._loadAndCompile(fragmentShaderFile, gl.GL_FRAGMENT_SHADER)

    def link(self):
        self.shaderProgram = gl.glCreateProgram()
        gl.glAttachShader(self.shaderProgram, self.vertexID)
        gl.glAttachShader(self.shaderProgram, self.fragmentID)
        gl.glLinkProgram(self.shaderProgram)
        if gl.glGetProgramiv(self.shaderProgram, gl.GL_LINK_STATUS) != gl.GL_TRUE:
            raise RuntimeError(gl.glGetProgramInfoLog(self.shaderProgram))
        gl.glDeleteShader(self.vertexID)
        gl.glDeleteShader(self.fragmentID)

    def setUniform_3f(self, name, f1, f2, f3):
        gl.glUniform3f(self._location(name), f1, f2, f3)

    def setUniform_4f(self, name, f1, f2, f3, f4):
        gl.glUniform4f(self._location(name), f1, f2, f3, f4)

    def setUniform_i(self, name, i):
        gl.glUniform1i(self._location(name), i)

    def setUniform_glmMat4(self, name, mat):
        gl.glUniformMatrix4fv(self._location(name), 1, gl.GL_FALSE, glm.value_ptr(mat))

    def setUniform_glmMat3(self, name, mat):
        gl.glUniformMatrix3fv(self._location(name), 1, gl.GL_FALSE, glm.value_ptr(mat))

    def setUniform_glmVec3(self, name, vec):
        gl.glUniform3f(self._location(name), vec.x, vec.y, vec.z)

    def setUniform_glmVec3_array(self, name, array):
        gl.glUniform3fv(self._location(name), len(array), array)

    def use(self):
        gl.glUseProgram(self.shaderProgram)

    def _location(self, name):
        if name not in self.cachedLocation:
            loc = gl.glGetUniformLocation(self.shaderProgram, name)
            if loc == -1:
                raise RuntimeError("GLSL uniform {} is unavailable".format(name))
            self.cachedLocation[name] = loc
        return self.cachedLocation[name]

    def _loadAndCompile(self, file, shaderType):
        shader = ""
        with open(file, "r") as shaderFile:
            shader = shaderFile.read()

        shaderID = gl.glCreateShader(shaderType)
        gl.glShaderSource(shaderID, shader)
        gl.glCompileShader(shaderID)
        if gl.glGetShaderiv(shaderID, gl.GL_COMPILE_STATUS) != gl.GL_TRUE:
            raise RuntimeError(gl.glGetShaderInfoLog(shaderID))

        return shader, shaderID
