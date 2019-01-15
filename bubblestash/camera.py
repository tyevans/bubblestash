import pyglet
from pyglet.gl import glViewport, glMatrixMode, gl, glLoadIdentity, glOrtho, glClearColor, glEnable, GL_BLEND, \
    glBlendFunc, GL_SRC_ALPHA, \
    GL_ONE_MINUS_SRC_ALPHA


class Camera(object):
    x = 0
    bottom = 0
    width = 640
    height = 480

    def __init__(self, left, bottom, width, height):
        self.left = left
        self.bottom = bottom
        self.init_gl(width, height)

    def screen_to_world_coords(self, x, y):
        return x + self.left, y + self.bottom

    def init_gl(self, width, height):
        # Set clear color
        self.width = width
        self.height = height
        glClearColor(0, 0, 0, 255)

        # Set alpha blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Set viewport
        glViewport(0, 0, self.width, self.height)

    def _update(self):
        # glViewport(0, 0, self.width, self.height)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(int(self.left), int(self.left + self.width), int(self.bottom), int(self.bottom + self.height), -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)

    def look_at(self, sprite: pyglet.sprite.Sprite):
        self.left = int(sprite.x - self.width // 2)
        self.bottom = int(sprite.y - self.height // 2)
        self._update()

    def update(self, left=None, bottom=None, width=None, height=None):
        self.left = left or self.left
        self.bottom = bottom or self.bottom
        self.width = width or self.width
        self.height = height or self.height
        self._update()
