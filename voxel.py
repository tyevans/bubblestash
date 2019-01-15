from itertools import zip_longest

import pyglet
from pyglet.gl import glEnable, glBlendFunc, GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_TEXTURE_2D, \
    glTexParameteri, GL_TEXTURE_MAG_FILTER, GL_NEAREST, GL_TEXTURE_MIN_FILTER
from pyglet.window import key

from bubblestash import controls
from bubblestash.camera import Camera
from bubblestash.window import GameWindow

glEnable(GL_TEXTURE_2D)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

voxels_image = pyglet.resource.image("data/images/voxels.png")
voxels_sequence = pyglet.image.ImageGrid(voxels_image, 1, 16)

tex = voxels_image.get_texture()
glTexParameteri(tex.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
glTexParameteri(tex.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


class Voxel(pyglet.sprite.Sprite):

    def __init__(self, x, y, value=0, shape_value=0):
        self.value = value
        self.shape_value = shape_value
        super().__init__(img=voxels_sequence[self.shape_value], x=x * 32, y=y * 32)


class VoxelGrid(object):

    def __init__(self, x, y, width, height, state=None, neighbor_x=None, neighbor_y=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.state = state or ([0] * (width * height))
        self.neighbor_x = neighbor_x
        self.neighbor_y = neighbor_y

        self._sprite_cache = []
        self.update_sprite_cache()

    def get_state_at(self, x, y):
        if x < self.x + self.width:
            if y < self.y + self.height:
                i = (y - self.y) * self.width + (x - self.x)
                return self.state[i]
            elif self.neighbor_y is not None:
                return self.neighbor_y.get_state_at(x, y)
            else:
                return 0
        elif self.neighbor_x is not None:
            return self.neighbor_x.get_state_at(x, y)
        else:
            return 0

    def get_shape_state_at(self, x, y):
        return sum([
            self.get_state_at(x, y),
            self.get_state_at(x + 1, y) * 2,
            self.get_state_at(x + 1, y + 1) * 4,
            self.get_state_at(x, y + 1) * 8,
        ])

    def update_sprite_cache(self, hard=False):
        _new_cache = []
        for i, (value, voxel) in enumerate(zip_longest(self.state, self._sprite_cache)):
            x = self.x + i % self.width
            y = self.y + i // self.width
            shape_value = self.get_shape_state_at(x, y)
            if shape_value:
                inst = Voxel(x, y, value=value, shape_value=shape_value)
                _new_cache.append(inst)
        self._sprite_cache = _new_cache

    def __setitem__(self, key, value):
        x, y = key
        x = x - self.x
        y = y - self.y
        i = y * self.width + x
        self.state[i] = value
        self.update_sprite_cache()

    def draw(self):
        for voxel in self._sprite_cache:
            voxel.draw()


class VoxelMap(object):

    def __init__(self, width=64, height=64, grid_width=8, grid_height=8, cell_height=32, cell_width=32):
        self.width = width
        self.height = height
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_width = cell_width
        self.cell_height = cell_height

        self._grids = []

        _prev_row = None
        for y in range(0, height, grid_height):
            row = []
            _prev_grid = None
            for i, x in enumerate(range(0, width, grid_width)):
                grid = VoxelGrid(x, y, self.grid_width, self.grid_height)
                if _prev_grid is not None:
                    _prev_grid.neighbor_x = grid
                if _prev_row is not None:
                    _prev_row[i].neighbor_y = grid
                _prev_grid = grid
                row.append(grid)
            self._grids.extend(row)
            _prev_row = row

        for grid in self._grids:
            grid.update_sprite_cache(True)

    def get_grid_at(self, x, y):
        i = y // self.grid_height * (self.width // self.grid_height) + (x // self.grid_width)
        return self._grids[i]

    def draw(self, camera=None):
        if camera:
            left = camera.left // self.cell_width
            right = (camera.left + camera.width) // self.cell_width
            bottom = camera.bottom // self.cell_height
            top = (camera.bottom + camera.height) // self.cell_height

            for grid in self._grids:
                far_x = grid.x + grid.width
                far_y = grid.y + grid.height
                if (left <= grid.x <= right or left <= far_x <= right) and \
                        (bottom <= grid.y <= top or bottom <= far_y <= top):
                    grid.draw()
        else:
            for grid in self._grids:
                grid.draw()

    def __setitem__(self, key, value):
        x, y = key
        grid = self.get_grid_at(x, y)
        grid[x, y] = value

        if x > 0:
            self.get_grid_at(x - 1, y)
            if y > 0:
                self.get_grid_at(x - 1, y - 1)
        if y > 0:
            self.get_grid_at(x - 1, y - 1)


if __name__ == "__main__":
    import cv2

    CAMERA_MOVE_SPEED = 300

    camera = Camera(0, 0, 1280, 720)
    window = GameWindow(width=1280, height=720, camera=camera)

    input_handler = controls.KeyboardInputHandler({
        key.UP: "CAMERA_UP",
        key.LEFT: "CAMERA_LEFT",
        key.DOWN: "CAMERA_DOWN",
        key.RIGHT: "CAMERA_RIGHT",
    })

    map = VoxelMap()


    @window.event
    def on_key_press(symbol, modifiers):
        return input_handler.on_key_press(symbol, modifiers)


    @window.event
    def on_key_release(symbol, modifiers):
        return input_handler.on_key_release(symbol, modifiers)


    @window.event
    def on_mouse_release(x, y, button, modifiers):
        _x = (camera.left + x) // 32
        _y = (camera.bottom + y) // 32
        map[_x, _y] = 1


    img = cv2.imread("./data/images/example_level.png")
    height, width = img.shape[:2]

    for y, col in enumerate(reversed(img)):
        for x, cell in enumerate(col):
            map[x, y] = cell[0] == 0

    for grid in map._grids:
        grid.update_sprite_cache(True)


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
