import pyglet
import pymunk
from pyglet.window import key, mouse

from bubblestash import Actor, KeyboardInputHandler, Stage, Camera, GameWindow, Player


def create_platform(x=0, y=0, width=20, height=20):
    box_image = pyglet.resource.image("data/images/box.png")
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    start = (0, height)
    end = (width, height)
    segment = pymunk.Segment(body, start, end, 0.0)
    segment.elasticity = 1.
    segment.friction = 0.5
    platform = Actor(img=box_image, x=x, y=y, body=body, shape=segment)
    platform.update(scale_x=width / 20, scale_y=height / 20)
    return platform


def create_falling_circle(x, y):
    circle_image = pyglet.resource.image("data/images/circle.png")
    circle_image.anchor_x = 15
    circle_image.anchor_y = 15

    body = pymunk.Body(mass=2, moment=1000)
    body.center_of_gravity = (.5, .5)

    poly = pymunk.Circle(body, radius=15)
    poly.elasticity = .9
    poly.friction = 0.8

    return Actor(img=circle_image, x=x, y=y, body=body, shape=poly)


def create_player(x, y):
    box_image = pyglet.resource.image("data/images/box2.png")
    box_image.anchor_x = 10
    box_image.anchor_y = 10
    body = pymunk.Body(mass=5, moment=1000)
    body.center_of_gravity = (.5, 0)
    poly = pymunk.Poly.create_box(body, size=(20, 20))
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

    stage.add_actor(create_platform(280, 50, width=720, height=20))

    player = create_player(300, 90)
    stage.add_actor(player)


    @window.event
    def on_mouse_release(x, y, button, modifiers):
        _x, _y = camera.screen_to_world_coords(x, y)
        if button == mouse.LEFT:
            box = create_falling_circle(_x, _y)
            stage.add_actor(box)

        if button == mouse.RIGHT:
            shape = stage.space.point_query((_x, _y), pymunk.inf, pymunk.ShapeFilter())
            print(shape)
            # stage.space.gravity = 0, -stage.space.gravity[1]


    def update(dt):
        stage.act(dt)
        camera.look_at(player)

        window.clear()
        stage.draw()


    pyglet.clock.schedule_interval(update, 1 / 144.0)
    pyglet.app.run()
