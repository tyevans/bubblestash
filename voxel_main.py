import cv2
import pyglet
from pyglet.window import key, mouse

from bubblestash import controls
from bubblestash.camera import Camera
from bubblestash.window import GameWindow
from voxels.map import VoxelMap
from voxels.perlin import generate_random_map
from voxels.voxel import EMPTY_VOXEL, DirtVoxel, MarbleVoxel, DiamondVoxel, IronVoxel

if __name__ == "__main__":

    CAMERA_MOVE_SPEED = 300

    camera = Camera(0, 0, 1280, 720)
    window = GameWindow(width=1280, height=720, camera=camera)

    input_handler = controls.KeyboardInputHandler({
        key.UP: "CAMERA_UP",
        key.LEFT: "CAMERA_LEFT",
        key.DOWN: "CAMERA_DOWN",
        key.RIGHT: "CAMERA_RIGHT",
    })


    @window.event
    def on_key_press(symbol, modifiers):
        return input_handler.on_key_press(symbol, modifiers)


    @window.event
    def on_key_release(symbol, modifiers):
        return input_handler.on_key_release(symbol, modifiers)


    map_state = generate_random_map(32, 32, {
        DirtVoxel: 0.8,
        MarbleVoxel: 0.1,
        DiamondVoxel: 0.005,
        IronVoxel: 0.06
    })
    # map_state = cv2.imread("./data/images/example_level.png")
    map = VoxelMap(state=map_state)


    @window.event
    def on_mouse_release(x, y, button, modifiers):
        _x = int(camera.left + x) // 32
        _y = int(camera.bottom + y) // 32
        if button == mouse.LEFT:
            map[_x, _y] = (0, 0, 0)
        if button == mouse.RIGHT:
            map[_x, _y] = EMPTY_VOXEL


    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        _x = int(camera.left + x) // 32
        _y = int(camera.bottom + y) // 32
        if buttons == mouse.LEFT:
            map[_x, _y] = (0, 0, 0)
        if buttons == mouse.RIGHT:
            map[_x, _y] = EMPTY_VOXEL


    def update(dt):
        delta_left = 0
        delta_bottom = 0

        if input_handler.key_down("CAMERA_LEFT"):
            delta_left -= dt * CAMERA_MOVE_SPEED
        if input_handler.key_down("CAMERA_RIGHT"):
            delta_left += dt * CAMERA_MOVE_SPEED
        if input_handler.key_down("CAMERA_UP"):
            delta_bottom += dt * CAMERA_MOVE_SPEED
        if input_handler.key_down("CAMERA_DOWN"):
            delta_bottom -= dt * CAMERA_MOVE_SPEED

        if delta_left or delta_bottom:
            camera.update(
                left=camera.left + delta_left,
                bottom=camera.bottom + delta_bottom
            )

        window.clear()
        map.draw(camera)


    pyglet.clock.schedule_interval(update, 1 / 144.0)
    pyglet.app.run()
