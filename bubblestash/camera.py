import pyglet
from pyglet import gl


class Camera(object):
    x = 0
    bottom = 0
    width = 640
    height = 480
    follow_speed = 300

    def __init__(self, left, bottom, width, height, zoom=1.):
        self.left = left
        self.bottom = bottom

        self.target_left = left
        self.target_bottom = bottom

        self.width = width
        self.height = height
        self.half_width = self.width / 2
        self.half_height = self.height / 2
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

        return int(scaled_left), int(scaled_right), int(scaled_bottom), int(scaled_top)

    def screen_to_world_coords(self, x, y):
        scaled_left, scaled_right, scaled_bottom, scaled_top = self.scaled_bounds()
        scaled_width = scaled_right - scaled_left
        scaled_height = scaled_top - scaled_bottom
        world_x = int(x * scaled_width / self.width + scaled_left)
        world_y = int(y * scaled_height / self.height + scaled_bottom)
        return world_x, world_y

    def init_gl(self):
        # Set clear color
        gl.glClearColor(.3, .3, .3, 1.)

        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # Set viewport
        # gl.glViewport(0, 0, self.width, self.height)
        # self._update()

    def _update(self):
        # glViewport(0, 0, self.width, self.height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        scaled_left, scaled_right, scaled_bottom, scaled_top = self.scaled_bounds()
        gl.glOrtho(
            scaled_left,
            scaled_right,
            scaled_bottom,
            scaled_top,
            -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def look_at(self, sprite: pyglet.sprite.Sprite, animate=True):
        if animate:
            left = int(sprite.x - self.width // 2)
            bottom = int(sprite.y - self.height // 2)
            self.update(left=left, bottom=bottom)
        else:
            self.left = int(sprite.x - self.width // 2)
            self.bottom = int(sprite.y - self.height // 2)
            self._update()

    def update(self, left=None, bottom=None, width=None, height=None, zoom=None):
        self.target_left = left or self.left
        self.target_bottom = bottom or self.bottom
        if width or height:
            self.width = width or self.width
            self.height = height or self.height
            self.half_width = self.width / 2
            self.half_height = self.height / 2
        self.zoom = zoom or self.zoom
        self._update()

    def act(self, dt):
        dirty = False
        if self.target_left != self.left:
            dirty = True
            if self.left < self.target_left:
                distance = self.target_left - self.left
                direction = 1
            else:
                distance = self.left - self.target_left
                direction = -1

            travel = min(distance, self.follow_speed * dt)
            self.left += travel * direction

        if self.target_bottom != self.bottom:
            dirty = True
            if self.bottom < self.target_bottom:
                distance = self.target_bottom - self.bottom
                direction = 1
            else:
                distance = self.bottom - self.target_bottom
                direction = -1

            travel = min(distance, self.follow_speed * dt)
            self.bottom += travel * direction
        if dirty:
            self._update()