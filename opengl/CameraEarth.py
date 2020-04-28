import glm
import glfw

import math


class CameraEarth:
    def __init__(self, window):
        self.radius = 20
        self.pos = glm.vec3(0, 0, 3)
        self.front = glm.vec3(0, 0, -1)
        self.up = glm.vec3(0, 1, 0)

        self.speed = 25
        self.sensitivity = 0.1

        self.fov = 45
        self._fov_cursor = 0

        self._lastX = None
        self._lastY = None
        self.yaw = -90
        self.pitch = 0

        self._window = window

    def view(self):
        return glm.lookAt(self.pos, glm.vec3(0, 0, 0), self.up)

    def projection(self):
        return glm.perspective(glm.radians(self.fov), self._window.width / self._window.height, 0.1, 1000)

    def processInput(self, window, deltaTime):
        delta = self.speed * deltaTime
        calc = False
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            self.radius -= delta
            calc = True
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            self.radius += delta
            calc = True

        if calc:
            self.pos = self.radius * glm.vec3(math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch)),
                math.sin(glm.radians(self.pitch)),
                math.sin(glm.radians(self.yaw) * math.cos(glm.radians(self.pitch))))

    def processMouse(self, xpos, ypos):
        if self._lastX is None or self._lastY is None:
            self._lastX = xpos
            self._lastY = ypos

        xoffset = xpos - self._lastX
        yoffset = self._lastY - ypos
        self._lastX = xpos
        self._lastY = ypos

        xoffset *= self.sensitivity
        yoffset *= self.sensitivity

        self.yaw = glm.mod(self.yaw + xoffset, 360)
        self.pitch += yoffset
        self.pitch = min(self.pitch, 89.0)
        self.pitch = max(self.pitch, -89.0)

        self.pos = self.radius * glm.vec3(math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch)),
                math.sin(glm.radians(self.pitch)),
                math.sin(glm.radians(self.yaw) * math.cos(glm.radians(self.pitch))))

    def processScroll(self, xoffset, yoffset):
        self._fov_cursor -= yoffset/10
        self.fov = (math.atan(self._fov_cursor)/math.pi+0.5)*90
