from collections import deque

import pyglet


class ExplosionGenerator(object):

    def __init__(self):
        explosion = pyglet.image.load('data/images/explosion.png')
        explosion_seq = pyglet.image.ImageGrid(explosion, 1, 8)

        frames = []
        for image in explosion_seq:
            frame = pyglet.image.AnimationFrame(image, .025)
            frames.append(frame)

        self.animation = pyglet.image.Animation(frames)
        self._texture_bin = pyglet.image.atlas.TextureBin()
        self.animation.add_to_texture_bin(self._texture_bin)

    def gen_explosion(self, x, y):
        sprite = pyglet.sprite.Sprite(img=self.animation, x=x - 16, y=y - 16)
        return sprite


window = pyglet.window.Window()
explosion_gen = ExplosionGenerator()
explosions = deque(maxlen=256)


@window.event
def on_draw():
    window.clear()
    for e in explosions:
        e.draw()


@window.event
def on_mouse_motion(x, y, dx, dy):
    explosion = explosion_gen.gen_explosion(x, y)
    explosions.append(explosion)


pyglet.app.run()
