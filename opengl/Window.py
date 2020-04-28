import time
import sys

from OpenGL import GL as gl
import glfw


class Window:
    def __init__(self, width, height, title, vmajor=3, vminor=3):
        self.width = width
        self.height = height
        self.title = title

        self.fps_limiter = None
        self._startTime = time.perf_counter()

        self.print_fps = False
        self._num_fps = 0
        self._print_time = None
        self.print_interval = 1

        self.camera = None
        # Speed control
        self.speed = 1
        self.pressed = {"left": False, "right": False}

        self._deltaTime = time.perf_counter()

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, vmajor)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, vminor)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.SAMPLES, 4)

        # Special case for backward compatibility in macOS
        if sys.platform == "darwin":
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

        self.window = glfw.create_window(self.width, self.height, title, None, None)
        if not self.window:
            raise RuntimeError("Cannot create a glfw window.")

        glfw.make_context_current(self.window)

        gl.glViewport(0, 0, self.width, self.height)
        glfw.set_framebuffer_size_callback(self.window, self._framebufferSizeCallback)
        glfw.set_cursor_pos_callback(self.window, self._mouseCallback)
        glfw.set_scroll_callback(self.window, self._scrollCallback)

        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def end(self):
        glfw.terminate()

    def opened(self):
        return not glfw.window_should_close(self.window)

    def renderLoopStart(self):
        if self.print_fps:
            now = time.perf_counter()
            if self._print_time is None:
                self._print_time = now
            elif now - self._print_time >= self.print_interval:
                print("                       ", end='\r')
                print("FPS: {}".format(self._num_fps/(now-self._print_time)), end='\r')
                self._print_time = now
                self._num_fps = 0
            self._num_fps += 1

        self._deltaTime = time.perf_counter() - self._startTime
        self._startTime = time.perf_counter()

    def renderLoopEnd(self):
        glfw.swap_buffers(self.window)
        glfw.poll_events()
        if self.fps_limiter is not None and self._startTime is not None:
            time.sleep(max(1./self.fps_limiter - (time.perf_counter() - self._startTime), 0))

    def processInput(self):
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)
        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        else:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

        # Speed managment
        leftPressed = glfw.get_key(self.window, glfw.KEY_LEFT)
        if leftPressed == glfw.PRESS:
            if not self.pressed["left"]:
                if self.speed <= 1/16:
                    self.speed = 0
                else:
                    self.speed /= 2
                    if self.speed > 1:
                        self.speed = round(self.speed)
                    self.speed = max(self.speed, 1/16)
        self.pressed["left"] = leftPressed

        rightPressed = glfw.get_key(self.window, glfw.KEY_RIGHT)
        if rightPressed == glfw.PRESS:
            if not self.pressed["right"]:
                if self.speed == 0:
                    self.speed = 1/16
                else:
                    self.speed *= 2
                    if self.speed > 1:
                        self.speed = round(self.speed)
                    self.speed = min(self.speed, 2**10)
        self.pressed["right"] = rightPressed

        if self.camera is not None:
            self.camera.processInput(self.window, self._deltaTime)

    def _framebufferSizeCallback(self, window, width, height):
        self.width, self.height = width, height
        gl.glViewport(0, 0, width, height)

    def _mouseCallback(self, window, xpos, ypos):
        if self.camera is not None:
            self.camera.processMouse(xpos, ypos)

    def _scrollCallback(self, window, xoffset, yoffset):
        if self.camera is not None or False:
            self.camera.processScroll(xoffset, yoffset)
