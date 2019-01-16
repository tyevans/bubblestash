import pyglet
import pymunk
from pyglet.gl import glEnable, glTexParameteri, glBlendFunc, GL_SRC_ALPHA, GL_BLEND, GL_TEXTURE_2D, \
    GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_NEAREST, GL_ONE_MINUS_SRC_ALPHA
from pyglet.window import key, mouse

from bubblestash import actor, controls
from bubblestash.camera import Camera
from bubblestash.stage import Stage
from bubblestash.window import GameWindow
from quote import SpeechBubble

glEnable(GL_TEXTURE_2D)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


class CollisionTypes(object):
    PLATFORM = 0b00000001
    PLAYER = 0b00000010
    PLAYER_BULLET = 0b00000100
    ENEMY_BULLET = 0b00001000
    ENEMY = 0b00010000
    POWERUP = 0b00100000
    PROP = 0b01000000
    SIGN = 0b10000000

class CollisionMasks(object):
    PLATFORM = 0b11111110
    PLAYER = 0b10111001
    PLAYER_BULLET = 0b01010001
    ENEMY_BULLET = 0b00000000

class Player(actor.Actor):
    speed = 300
    jump_speed = 3000
    jump_duration = 0.2

    def __init__(self, input_handler, *args, **kwargs):
        player_image = pyglet.resource.image('data/images/player.png')
        player_img_seq = pyglet.image.ImageGrid(player_image, 1, 3)

        frames = []
        for i, image in enumerate(player_img_seq):
            image.anchor_x = 32
            image.anchor_y = 64
            frame = pyglet.image.AnimationFrame(image, .25)
            frames.append(frame)
        frames.append(pyglet.image.AnimationFrame(player_img_seq[1], .25))

        self.animation = pyglet.image.Animation(frames)

        self.jump_time = 0
        self.input_handler = input_handler
        body = pymunk.Body(mass=5, moment=10000)
        body.center_of_gravity = (.5, .5)
        poly = pymunk.Poly.create_box(body, size=(64, 128))
        poly.elasticity = .3
        poly.friction = 0.1
        poly.collision_type = CollisionTypes.PLAYER
        super().__init__(img=self.animation, body=body, shape=poly, *args, **kwargs)

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


class Boulder(actor.Actor):

    def __init__(self, radius=30, *args, **kwargs):
        circle_image = pyglet.resource.image("data/images/circle.png")
        circle_image.anchor_x = 32
        circle_image.anchor_y = 32

        body = pymunk.Body(mass=2, moment=10000)
        body.center_of_gravity = (.5, .5)

        poly = pymunk.Circle(body, radius=radius)
        poly.elasticity = .9
        poly.friction = 0.8
        poly.collision_type = CollisionTypes.PROP
        super().__init__(img=circle_image, body=body, shape=poly, *args, **kwargs)


class Platform(actor.Actor):

    def __init__(self, width=512, height=64, *args, **kwargs):
        box_image = pyglet.resource.image("data/images/platform.png")
        box_image.anchor_x = 256
        box_image.anchor_y = 32
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.center_of_gravity = (0.5, 0.5)
        poly = pymunk.Poly.create_box(body, size=(width, height))
        poly.elasticity = 1.
        poly.friction = 0.5
        poly.collision_type = CollisionTypes.PLATFORM
        super().__init__(img=box_image, body=body, shape=poly, *args, **kwargs)
        self.update(scale_x=width / 512, scale_y=height / 64)


class Sign(actor.Actor):

    def __init__(self, *args, **kwargs):
        sign_image = pyglet.image.load("./data/images/sign.png")
        sign_image.anchor_x = 32
        sign_image.anchor_y = 64

        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.center_of_gravity = (0.5, 0.5)
        poly = pymunk.Poly.create_box(body, size=(64, 128))
        poly.collision_type = CollisionTypes.SIGN
        super().__init__(img=sign_image, body=body, shape=poly, *args, **kwargs)


if __name__ == "__main__":
    input_handler = controls.KeyboardInputHandler({
        key.W: "UP",
        key.A: "LEFT",
        key.S: "DOWN",
        key.D: "RIGHT",
        key.SPACE: "JUMP",
        key.UP: "CAMERA_UP",
        key.LEFT: "CAMERA_LEFT",
        key.DOWN: "CAMERA_DOWN",
        key.RIGHT: "CAMERA_RIGHT",
    })

    camera = Camera(0, 0, 1280, 720)
    camera.init_gl()
    window = GameWindow(width=1280, height=720, camera=camera)

    stage = Stage()
    stage.space.gravity = 0, -900

    sign = Sign(x=632, y=295)
    stage.add_actor(sign)

    stage.add_actor(Platform(x=280, y=50))

    stage.add_actor(Platform(x=700, y=200))

    player = Player(input_handler, x=300, y=300)
    stage.add_actor(player)

    props = []


    def pre_solve(arbiter, space, data):
        if arbiter.is_first_contact:
            bubble = SpeechBubble(650, 360, "This sign has important things to say!")
            props.append(bubble)
        return False


    def separate(arbiter, space, data):
        del props[::]


    def ignore_collision(*args, **kwargs):
        return False


    handler = stage.space.add_collision_handler(CollisionTypes.PLAYER, CollisionTypes.SIGN)
    handler.pre_solve = pre_solve
    handler.separate = separate

    handler = stage.space.add_collision_handler(CollisionTypes.PROP, CollisionTypes.SIGN)
    handler.pre_solve = ignore_collision


    @window.event
    def on_key_press(symbol, modifiers):
        return input_handler.on_key_press(symbol, modifiers)


    @window.event
    def on_key_release(symbol, modifiers):
        return input_handler.on_key_release(symbol, modifiers)


    @window.event
    def on_mouse_release(x, y, button, modifiers):
        _x, _y = camera.screen_to_world_coords(x, y)
        if button == mouse.LEFT:
            box = Boulder(x=_x, y=_y)
            stage.add_actor(box)

        if button == mouse.RIGHT:
            print(_x, _y)
            # shape = stage.space.point_query_nearest((_x, _y), pymunk.inf, pymunk.ShapeFilter())
            # print(shape)
            # stage.space.gravity = 0, -stage.space.gravity[1]


    def update(dt):
        stage.act(dt)
        camera.look_at(player)
        window.clear()
        stage.draw()
        for prop in props:
            prop.draw()


    pyglet.clock.schedule_interval(update, 1 / 144.0)
    pyglet.app.run()
