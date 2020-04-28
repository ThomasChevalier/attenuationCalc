import numpy as np
import datetime
import time

import glfw
from OpenGL import GL as gl
import glm

from opengl import Shaders
from opengl import Window
from opengl import Texture
from opengl import CameraFly
from opengl import Sphere

from opengl import load_from_file


def replace_tag(tag, value, file):
    """Replaces a tag in a file with the specified value and returns a new file name."""
    with open(file, "r") as origin:
        with open(file+".replaced", "w") as dest:
            dest.write(origin.read().replace(tag, str(value)))
    return file+".replaced"


def view3D(context):

    if not glfw.init():
        raise RuntimeError("Cannot initialize glfw.")

    window = Window(800, 600, "3D visualization")
    window.fps_limiter = 60
    window.print_fps = False

    print("Move wth ZQSD keys and mouse.")
    print("Use Left and Right keys to change speed of the visualization")
    print("In-sight relays are in green, other one in red.")
    print("Targeted satellite is white.")

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_MULTISAMPLE)

    # Camera
    camera = CameraFly(window)
    window.camera = camera

    # Loading file
    print("[  ] Loading file", end='\r')
    sat, relays, t0, tmax = load_from_file(context.visualization_file)
    offset = 0
    print("[OK] Loading file")

    # Vertex shader
    print("[  ] Compiling shaders", end='\r')
    lightingShader  = Shaders("opengl/shader_light.vs", "opengl/shader_light.fs")
    satelliteShader = Shaders(replace_tag("#satellites_number#", 1+len(relays), "opengl/shader_sat.vs"),   "opengl/shader_sat.fs")
    print("[OK] Compiling shaders")

    # Texture
    print("[  ] Loading textures", end='\r')
    earthTexture = Texture("opengl/textures/earthBig_2.jpg", 0)
    print("[OK] Loading textures")

    # Meshes
    print("[  ] Generating meshes", end='\r')
    earthMesh = Sphere((0, 0, 0), 128, 64, 1)
    sphereLow = Sphere((0, 0, 0), 16, 8, 0.01)
    print("[OK] Generating meshes")

    # Shader setup

    lightingShader.use()
    lightingShader.setUniform_i("texture1", earthTexture.unit)

    gl.glClearColor(0.5, 0.5, 0.5, 1.0)

    satellitesPositions = np.empty((3*(1+len(relays)),), dtype='float32')
    satellitesColors    = np.empty((3*(1+len(relays)),), dtype='float32')

    lastPrint = 0

    while window.opened():
        window.renderLoopStart()
        window.processInput()

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        lightingShader.use()
        lightingShader.setUniform_glmMat4("view", camera.view())
        lightingShader.setUniform_glmMat4("projection", camera.projection())
        model = glm.mat4(1.0)
        lightingShader.setUniform_glmMat4("model", model)
        earthTexture.bind()
        earthMesh.draw()

        satelliteShader.use()
        satelliteShader.setUniform_glmMat4("view", camera.view())
        satelliteShader.setUniform_glmMat4("projection", camera.projection())

        # Draw satellites
        t = t0+(glfw.get_time()-offset)*window.speed
        if t >= tmax:
            offset = glfw.get_time()
            t = t0

        if time.time() - lastPrint > 0.05:
            speedStr = str(window.speed)+"x" if window.speed != 0 else "paused"
            print("Speed: {:^10} - Time {}".format(speedStr, datetime.datetime.utcfromtimestamp(t)), end='\r')
            lastPrint = time.time()

        position = sat.posToScene(sat.at(t), earthMesh.offset_x, earthMesh.offset_y, earthMesh.offset_z, earthMesh.radius)
        satellitesPositions[0:3] = position
        satellitesColors[0:3] = glm.vec3(1, 1, 1)
        for i, relay in enumerate(relays):
            state = relay.at(t)
            satellitesPositions[3*(i+1):3*(i+2)] = relay.posToScene(state, earthMesh.offset_x, earthMesh.offset_y, earthMesh.offset_z, earthMesh.radius)
            los = state[3]
            satellitesColors[3*(i+1):3*(i+2)] = glm.vec3((1-los), los, 0)
        satelliteShader.setUniform_glmVec3_array("offsets", satellitesPositions)
        satelliteShader.setUniform_glmVec3_array("colors", satellitesColors)
        sphereLow.drawInstanced(1+len(relays))

        window.renderLoopEnd()

    window.end()
