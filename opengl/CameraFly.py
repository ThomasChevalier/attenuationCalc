import glm
import glfw

import math


class CameraFly:
    def __init__(self, window):
        self.pos = glm.vec3(0, 0, 3)
        self.front = glm.vec3(0, 0, -1)
        self.up = glm.vec3(0, 1, 0)

        self.speed = 5
        self.sensitivity = 0.1

        self.fov = 45
        self._fov_cursor = 0

        self._lastX = None
        self._lastY = None
        self._yaw = -90
        self._pitch = 0

        self._window = window

    def view(self):
        return glm.lookAt(self.pos, self.pos + self.front, self.up)

    def projection(self):
        return glm.perspective(glm.radians(self.fov), self._window.width / self._window.height, 0.1, 1000)

    def processInput(self, window, deltaTime):
        delta = self.speed * deltaTime
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            self.pos += delta * self.front
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            self.pos -= delta * self.front
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            self.pos -= glm.normalize(glm.cross(self.front, self.up)) * delta
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            self.pos += glm.normalize(glm.cross(self.front, self.up)) * delta

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

        self._yaw = glm.mod(self._yaw + xoffset, 360)
        self._pitch += yoffset

        self._pitch = min(self._pitch, 90.0)
        self._pitch = max(self._pitch, -90.0)

        direction = glm.vec3(
            math.cos(glm.radians(self._yaw)) * math.cos(glm.radians(self._pitch)),
            math.sin(glm.radians(self._pitch)),
            math.sin(glm.radians(self._yaw) * math.cos(glm.radians(self._pitch)))
            )
        self.front = glm.normalize(direction)
        # print("                                                                                                              ", end='\r')
        # print(self._yaw, self._pitch, xoffset, yoffset, end='\r')

    def processScroll(self, xoffset, yoffset):
        self._fov_cursor -= yoffset/10
        self.fov = (math.atan(self._fov_cursor)/math.pi+0.5)*90
        # print(self.fov)
