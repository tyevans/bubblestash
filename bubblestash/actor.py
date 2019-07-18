import pyglet


class Actor(pyglet.sprite.Sprite):
    def __init__(self, body, shape, x=0, y=0, *args, **kwargs):
        super().__init__(x=x, y=y, *args, **kwargs)
        self.body = body
        self.body.position = x, y
        self.shape = shape
        # self.shape.actor = self

    def act(self, dt):
        self.update(
            x=self.body.position.x,
            y=self.body.position.y,
            rotation=-self.body.rotation_vector.angle_degrees)
