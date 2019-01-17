import pyglet
from pyglet.gl import glViewport, glMatrixMode, gl, glLoadIdentity, glOrtho, glClearColor, glEnable, GL_BLEND, \
    glBlendFunc, GL_SRC_ALPHA, \
    GL_ONE_MINUS_SRC_ALPHA, glTexParameteri, GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST, GL_TEXTURE_MIN_FILTER


class Camera(object):
    x = 0
    bottom = 0
    width = 640
    height = 480

    def __init__(self, left, bottom, width, height, zoom=1.):
        self.left = left
        self.bottom = bottom
        self.width = width
        self.height = height
        self.zoom = zoom
        self.init_gl()

    def scaled_bounds(self):
        center_x = self.left + self.half_width
        center_y = self.bottom + self.half_height
        scaled_half_width = self.half_width * self.zoom
        scaled_half_height = self.half_height * self.zoom
        scaled_left = center_x - scaled_half_width
        scaled_right = center_x + scaled_half_width
        scaled_bottom = center_y - scaled_half_height
        scaled_top = center_y + scaled_half_height

        return scaled_left, scaled_right, scaled_bottom, scaled_top

    def screen_to_world_coords(self, x, y):
        scaled_left, scaled_right, scaled_bottom, scaled_top = self.scaled_bounds()
        scaled_width = scaled_right - scaled_left
        scaled_height = scaled_top - scaled_bottom
        print(scaled_width, scaled_height)
        world_x = int(x * scaled_width / self.width + scaled_left)
        world_y = int(y * scaled_height / self.height + scaled_bottom)
        return world_x, world_y

    def init_gl(self):
        # Set clear color
        glClearColor(255, 255, 255, 255)

        glEnable(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Set viewport
        glViewport(0, 0, self.width, self.height)

    def _update(self):
        # glViewport(0, 0, self.width, self.height)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        scaled_left, scaled_right, scaled_bottom, scaled_top = self.scaled_bounds()

        glOrtho(
            scaled_left,
            scaled_right,
            scaled_bottom,
            scaled_top,
            -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)

    def look_at(self, sprite: pyglet.sprite.Sprite):
        self.left = int(sprite.x - self.width // 2)
        self.bottom = int(sprite.y - self.height // 2)
        self._update()

    def update(self, left=None, bottom=None, width=None, height=None, zoom=None):
        self.left = left or self.left
        self.bottom = bottom or self.bottom
        if width or height:
            self.width = width or self.width
            self.height = height or self.height
            self.half_width = self.width / 2
            self.half_height = self.height / 2
        self.zoom = zoom or self.zoom
        self._update()
