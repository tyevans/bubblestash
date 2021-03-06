import numpy as np

import pyglet
import pymunk
from pyglet.window import key, mouse

from bubblestash import controls, actor
from bubblestash.camera import Camera
from bubblestash.stage import Stage
from bubblestash.window import GameWindow
from voxels.map import VoxelMap
from voxels.perlin import generate_random_map
from voxels.store import VoxelGridStore
from voxels.voxel import EMPTY_VOXEL, DiamondVoxel, DirtVoxel, MarbleVoxel, IronVoxel


class CollisionTypes(object):
    PLATFORM = 0b00000001
    PLAYER = 0b00000010
    PLAYER_BULLET = 0b00000100
    ENEMY_BULLET = 0b00001000
    ENEMY = 0b00010000
    POWERUP = 0b00100000
    PROP = 0b01000000
    SIGN = 0b10000000


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
        super().__init__(img=circle_image, body=body, shape=poly, *args, **kwargs)


class Player(actor.Actor):
    speed = 800
    airspeed = 300
    jump_speed = 3000
    jump_duration = 0.2

    def __init__(self, input_handler, *args, **kwargs):
        self.grounded = True
        player_image = pyglet.resource.image('data/images/smallest_pixel/Smallest Pixel - Run & Gun.png')
        self.player_img_seq = pyglet.image.ImageGrid(player_image, 1, 7)

        frames = []
        for i, image in enumerate(self.player_img_seq):
            image.anchor_x = 8
            image.anchor_y = 8
            frame = pyglet.image.AnimationFrame(image, .08)
            frames.append(frame)

        self.animation = pyglet.image.Animation(frames)

        self.jump_time = 0
        self.input_handler = input_handler
        body = pymunk.Body(mass=5, moment=10000)
        body.center_of_gravity = (.5, .5)
        poly = pymunk.Poly.create_box(body, size=(4, 12))
        poly.elasticity = .3
        poly.friction = 0.8
        poly.collision_type = CollisionTypes.PLAYER
        super().__init__(img=self.animation, body=body, shape=poly, *args, **kwargs)

    def act(self, dt):
        self.body.angle = 0
        speed = self.speed if self.grounded else self.airspeed
        moving = False
        if self.input_handler.key_down("LEFT"):
            moving = True
            if self.scale_x > 0:
                self.scale_x *= -1
            self.body.velocity -= (speed * dt, 0)

        if self.input_handler.key_down("RIGHT"):
            moving = True
            if self.scale_x < 0:
                self.scale_x *= -1
            self.body.velocity += (speed * dt, 0)

        if not moving and self.image != self.player_img_seq[0]:
            self.image = self.player_img_seq[0]
        elif self.image != self.animation:
            self.image = self.animation

        if self.input_handler.key_down("JUMP"):
            if self.jump_time > 0 or self.grounded:
                interval = min(dt, self.jump_time)
                if interval:
                    self.jump_time -= interval
                    self.body.velocity += (0, self.jump_speed * dt)
        else:
            if self.grounded:
                self.jump_time = self.jump_duration
            else:
                self.jump_time = 0
        super().act(dt)


if __name__ == "__main__":

    CAMERA_MOVE_SPEED = 300

    camera = Camera(0, 0, 1920, 1080, zoom=0.3)
    camera.init_gl()
    window = GameWindow(width=1920, height=1080, camera=camera)

    stage = Stage()
    space = stage.space
    stage.space.gravity = 0, -900
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
        key.LSHIFT: "CAMERA_ZOOM_MOD",
        key.ESCAPE: "EXIT_GAME"
    })


    @window.event
    def on_key_press(symbol, modifiers):
        return input_handler.on_key_press(symbol, modifiers)


    @window.event
    def on_key_release(symbol, modifiers):
        return input_handler.on_key_release(symbol, modifiers)


    maps = [generate_random_map(64, 64, {
        DirtVoxel: 0.2,
        IronVoxel: 0.2,
        DiamondVoxel: 0.2,
    }) for _ in range(2)]

    map_state = np.hstack(maps)
    # cv2.imwrite("./data/new_level.png", map_state)
    # map_state = cv2.imread("./data/new_level.png")
    map = VoxelMap(state=map_state, space=space)

    player = Player(input_handler, x=1024, y=2060)
    camera.look_at(player, animate=False)
    stage.add_actor(player)


    # image based loading
    # map_state = cv2.imread("./data/images/example_level.png")
    # map = VoxelMap(state=map_state, space=space)

    # Infinite random map
    # map = VoxelGridStore(space=space, known_voxels={
    #     DirtVoxel: 1.0,
    #     MarbleVoxel: 0.1,
    #     DiamondVoxel: 0.001,
    #     IronVoxel: 0.06
    # }, grid_width=32, grid_height=32)

    @window.event
    def on_mouse_release(x, y, button, modifiers):
        _x, _y = camera.screen_to_world_coords(x, y)
        x = _x // 32
        y = _y // 32 + 1
        if button == mouse.LEFT:
            if modifiers == 17:
                rock = Boulder(x=_x, y=_y)
                stage.add_actor(rock)
            else:
                map[x, y] = (0, 0, 0)
        if button == mouse.RIGHT:
            map[x, y] = EMPTY_VOXEL


    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        _x, _y = camera.screen_to_world_coords(x, y)
        x = _x // 32
        y = _y // 32 + 1
        if buttons == mouse.LEFT:
            map[x, y] = (0, 0, 0)
        if buttons == mouse.RIGHT:
            map[x, y] = EMPTY_VOXEL


    @window.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        if input_handler.key_down("CAMERA_ZOOM_MOD"):
            min_zoom = 0.1
            max_zoom = 5.0
            zoom = max(min(camera.zoom + (scroll_y / 10), max_zoom), min_zoom)
            camera.update(zoom=zoom)


    def pre_solve_platform(arbiter, space, data):
        player.grounded = True
        return True


    def separate(arbiter, space, data):
        player.grounded = False
        return True



    handler = stage.space.add_collision_handler(CollisionTypes.PLAYER, CollisionTypes.PLATFORM)
    handler.pre_solve = pre_solve_platform
    handler.separate = separate

    # label = FloatingLabel(camera, text="Ready!", font_name='Press Start 2P', font_size=64, x=0, y=0,
    #                       color=(0, 0, 0, 255), anchor_x='left',
    #                       anchor_y='bottom')

    camera.init_gl()


    def update(dt):
        delta_left = 0
        delta_bottom = 0

        # if input_handler.key_down("CAMERA_LEFT"):
        #     delta_left -= dt * CAMERA_MOVE_SPEED
        # if input_handler.key_down("CAMERA_RIGHT"):
        #     delta_left += dt * CAMERA_MOVE_SPEED
        # if input_handler.key_down("CAMERA_UP"):
        #     delta_bottom += dt * CAMERA_MOVE_SPEED
        # if input_handler.key_down("CAMERA_DOWN"):
        #     delta_bottom -= dt * CAMERA_MOVE_SPEED
        #
        # if delta_left or delta_bottom:
        #     camera.update(
        #         left=camera.left + delta_left,
        #         bottom=camera.bottom + delta_bottom
        #     )

        if input_handler.key_down("EXIT_GAME"):
            exit(0)
        stage.act(dt)
        camera.act(dt)
        camera.look_at(player)
        window.clear()
        map.draw(camera)
        stage.draw()
        # label.draw()


    pyglet.clock.schedule_interval(update, 1 / 60.0)
    pyglet.app.run()
