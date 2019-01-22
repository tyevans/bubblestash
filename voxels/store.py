import os
from functools import lru_cache

import cv2

from voxels.grid import VoxelGrid
from voxels.perlin import generate_random_map
from voxels.voxel import EMPTY_VOXEL


class VoxelGridProxy(VoxelGrid):
    def __init__(self, store, *args, **kwargs):
        self.store = store
        super().__init__(*args, **kwargs)

    @property
    def neighbor_x(self):
        return self.store[self.x + self.width, self.y]

    @property
    def neighbor_y(self):
        return self.store[self.x, self.y + self.height]


class VoxelGridStore(object):

    def __init__(self, space, state_dir="./data/state", grid_width=8, grid_height=8, known_voxels=None,
                 base_voxel=None):
        self._cache = {}
        self.space = space
        self.state_dir = state_dir
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.known_voxels = known_voxels or []
        self.base_voxel = base_voxel or EMPTY_VOXEL

    def _get_filename(self, x, y):
        filename = "{}_{}_{}_{}.png".format(x, y, self.grid_width, self.grid_height)
        return os.path.join(self.state_dir, filename)

    @lru_cache(1024)
    def __getitem__(self, item):
        x, y = item
        grid = self._cache.get((x, y))
        if not grid:
            filename = self._get_filename(x, y)
            if os.path.exists(filename):
                state = cv2.imread(filename)
            else:
                state = self.gen_state(x, y)
                self[x, y] = state

            grid = VoxelGridProxy(store=self, x=x, y=y, width=self.grid_width, height=self.grid_height, state=state, space=self.space)
            self._cache[(x, y)] = grid
        return grid

    def __setitem__(self, item, value):
        x, y = item
        filename = self._get_filename(x, y)
        cv2.imwrite(filename, value)

    def gen_state(self, x, y):
        return generate_random_map(self.grid_width, self.grid_height, self.known_voxels, base_voxel=self.base_voxel)

    def draw(self, camera):
        cam_left, cam_right, cam_bottom, cam_top = camera.scaled_bounds()
        grid_x_start = (cam_left // 32 - 1) // self.grid_width * self.grid_width
        grid_x_end = cam_right // 32 // self.grid_width * self.grid_width

        grid_y_start = (cam_bottom // 32 - 1) // self.grid_width * self.grid_width
        grid_y_end = cam_top // 32 // self.grid_width * self.grid_width

        padding_x = self.grid_width * 2
        padding_y = self.grid_height * 2
        grids = []
        for y in range(grid_y_start - padding_y, grid_y_end + padding_y, self.grid_height):
            for x in range(grid_x_start - padding_x, grid_x_end + padding_x, self.grid_width):
                grid = self[x, y]
                grids.append(grid)

        for grid in grids:
            grid.draw()
