import pyglet

from bubblestash.camera import Camera


class GameWindow(pyglet.window.Window):

    def __init__(self, camera=None, key_mapping=None, *args, **kwargs):
        self.key_mapping = key_mapping
        self.event_handlers = {}
        super().__init__(*args, **kwargs)
        self.camera = camera or Camera(0, 0, self.width, self.height)

    def on_resize(self, width, height):
        self.camera.update(width=self.width, height=self.height)