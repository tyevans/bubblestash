from pyglet.text import Label

class FloatingLabel(Label):

    def __init__(self, camera, *args, **kwargs):
        self.camera = camera
        super().__init__(*args, **kwargs)

    def draw(self):
        _x = self.x
        _y = self.y
        cam_x, _, cam_y, _ = self.camera.scaled_bounds()
        self.x = int((self.x / self.camera.zoom) + cam_x)
        self.y = int((self.y / self.camera.zoom) + cam_y)
        super().draw()
        self.x = _x
        self.y = _y