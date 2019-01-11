import pyglet
import pymunk
from pyglet.gl import glViewport, glMatrixMode, gl, glLoadIdentity, glOrtho, glClearColor, glEnable, GL_LINE_SMOOTH, \
    GL_POLYGON_SMOOTH, GL_LINE_SMOOTH_HINT, GL_NICEST, glHint, GL_BLEND, glBlendFunc, GL_SRC_ALPHA, \
    GL_ONE_MINUS_SRC_ALPHA


class KeyboardInputHandler(object):

    def __init__(self):
        self._key_states = {}

    def key_down(self, target):
        return self._key_states.setdefault(target, False)

    def set_on(self, target):
        self._key_states[target] = True

    def set_off(self, target):
        self._key_states[target] = False


class Stage(object):

    def __init__(self):
        self.space = pymunk.Space()
        self.actors = []
        self._batch = pyglet.graphics.Batch()

    def add_actor(self, actor: pyglet.sprite.Sprite):
        actor.batch = self._batch
        self.space.add(actor.body, actor.shape)
        self.actors.append(actor)

    def act(self, dt):
        self.space.step(dt)
        for actor in self.actors:
            actor.act(dt)

    def draw(self):
        for actor in self.actors:
            actor.draw()
        self._batch.draw()


class Actor(pyglet.sprite.Sprite):
    def __init__(self, body, shape, x=0, y=0, *args, **kwargs):
        super().__init__(x=x, y=y, *args, **kwargs)
        self.body = body
        self.body.position = x, y
        self.shape = shape
        self.shape.actor = self

    def act(self, dt):
        self.update(
            x=self.body.position.x,
            y=self.body.position.y,
            rotation=-self.body.rotation_vector.angle_degrees)


class Player(Actor):
    speed = 300
    jump_speed = 3000
    jump_duration = 0.2

    def __init__(self, body, shape, input_handler, x=0, y=0, *args, **kwargs):
        self.jump_time = 0
        super().__init__(body, shape, x, y, *args, **kwargs)
        self.input_handler = input_handler

    def act(self, dt):
        self.body.angle = 0
        if self.input_handler.key_down("LEFT"):
            self.body.velocity -= (self.speed * dt, 0)

        if self.input_handler.key_down("RIGHT"):
            self.body.velocity += (self.speed * dt, 0)

        if self.input_handler.key_down("JUMP"):
            interval = min(dt, self.jump_time)
            if interval:
                self.jump_time -= interval
                self.body.velocity += (0, self.jump_speed * dt)
        else:
            self.jump_time = self.jump_duration
        super().act(dt)


class GameWindow(pyglet.window.Window):

    def __init__(self, camera=None, input_handler=None, key_mapping=None, *args, **kwargs):
        self.input_handler = input_handler
        self.key_mapping = key_mapping
        self.event_handlers = {}
        super().__init__(*args, **kwargs)
        self.camera = camera or Camera(0, 0, self.width, self.height)

    def on_resize(self, width, height):
        self.camera.update(width=self.width, height=self.height)

    def on_key_press(self, symbol, modifiers):
        if self.input_handler:
            action = self.key_mapping.get(symbol)
            if action is not None:
                self.input_handler.set_on(action)

    def on_key_release(self, symbol, modifiers):
        if self.input_handler:
            action = self.key_mapping.get(symbol)
            if action is not None:
                self.input_handler.set_off(action)


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
        glClearColor(0 / 255, 0 / 255, 0 / 255, 0 / 255)

        # Set antialiasing
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        # Set alpha blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Set viewport
        glViewport(0, 0, self.width, self.height)

    def _update(self):
        # glViewport(0, 0, self.width, self.height)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.left, self.left + self.width, self.bottom, self.bottom + self.height, -1, 1)
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
