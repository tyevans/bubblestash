import pyglet
import pymunk
from pyglet.gl import glTexParameteri, GL_TEXTURE_MIN_FILTER, GL_NEAREST, GL_TEXTURE_MAG_FILTER
from pyglet.window import key, mouse

from bubblestash import Actor, KeyboardInputHandler, Stage, Camera, GameWindow, Player


def create_platform(x=0, y=0, width=512, height=64):
    box_image = pyglet.resource.image("data/images/platform.png")
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    start = (0, height)
    end = (width, height)
    segment = pymunk.Segment(body, start, end, 0.0)
    segment.elasticity = 1.
    segment.friction = 0.5
    platform = Actor(img=box_image, x=x, y=y, body=body, shape=segment)
    platform.update(scale_x=width / 512, scale_y=height / 64)
    return platform


def create_falling_circle(x, y):
    circle_image = pyglet.resource.image("data/images/circle.png")
    circle_image.anchor_x = 32
    circle_image.anchor_y = 32

    body = pymunk.Body(mass=2, moment=1000)
    body.center_of_gravity = (.5, .5)

    poly = pymunk.Circle(body, radius=30)
    poly.elasticity = .9
    poly.friction = 0.8

    return Actor(img=circle_image, x=x, y=y, body=body, shape=poly)


def create_player(x, y):
    box_image = pyglet.resource.image("data/images/player.png")
    box_image.anchor_x = 32
    box_image.anchor_y = 64
    body = pymunk.Body(mass=5, moment=1000)
    body.center_of_gravity = (.5, .5)
    poly = pymunk.Poly.create_box(body, size=(64, 128))
    poly.elasticity = .3
    poly.friction = 0.1
    return Player(img=box_image, body=body, shape=poly, input_handler=input_handler, x=x, y=y)


if __name__ == "__main__":
    input_handler = KeyboardInputHandler()

    key_mapping = {
        key.W: "UP",
        key.A: "LEFT",
        key.S: "DOWN",
        key.D: "RIGHT",
        key.SPACE: "JUMP",
        key.UP: "CAMERA_UP",
        key.LEFT: "CAMERA_LEFT",
        key.DOWN: "CAMERA_DOWN",
        key.RIGHT: "CAMERA_RIGHT",
    }

    stage = Stage()
    stage.space.gravity = 0, -900

    camera = Camera(0, 0, 1280, 720)
    window = GameWindow(width=1280, height=720, input_handler=input_handler, key_mapping=key_mapping,
                        camera=camera)

    stage.add_actor(create_platform(280, 50))

    stage.add_actor(create_platform(700, 200))

    player = create_player(300, 300)
    stage.add_actor(player)


    @window.event
    def on_mouse_release(x, y, button, modifiers):
        _x, _y = camera.screen_to_world_coords(x, y)
        if button == mouse.LEFT:
            box = create_falling_circle(_x, _y)
            stage.add_actor(box)

        if button == mouse.RIGHT:
            shape = stage.space.point_query_nearest((_x, _y), pymunk.inf, pymunk.ShapeFilter())
            print(shape)
            stage.space.gravity = 0, -stage.space.gravity[1]


    def update(dt):
        stage.act(dt)
        camera.look_at(player)

        window.clear()
        stage.draw()


    pyglet.clock.schedule_interval(update, 1 / 60.0)
    pyglet.app.run()
