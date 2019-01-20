import pyglet
import pymunk


class Stage(object):

    def __init__(self):
        self.space = pymunk.Space()
        self.actors = []
        self._batch = pyglet.graphics.Batch()

    def add_actor(self, actor: pyglet.sprite.Sprite):
        actor.batch = self._batch
        self.space.add(actor.body, actor.shape)
        self.actors.append(actor)

    def remove_actor(self, actor):
        self.space.remove(actor.body, actor.shape)
        self.actors.remove(actor)

    def act(self, dt):
        self.space.step(dt)
        for actor in self.actors:
            actor.act(dt)

    def draw(self):
        self._batch.draw()

