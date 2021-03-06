from voxels.grid import VoxelGrid


class VoxelMap(object):

    def __init__(self, state, space, grid_width=8, grid_height=8, cell_height=32, cell_width=32):
        self.height, self.width = state.shape[:2]
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.space = space

        self._grids = []

        _prev_row = None
        for y in range(0, self.height, grid_height):
            row = []
            _prev_grid = None
            for i, x in enumerate(range(0, self.width, grid_width)):
                grid_state = state[y:y + self.grid_height, x:x + self.grid_width]
                grid = VoxelGrid(x, y, self.grid_width, self.grid_height, space=self.space, state=grid_state)
                if _prev_grid is not None:
                    _prev_grid.neighbor_x = grid
                if _prev_row is not None:
                    _prev_row[i].neighbor_y = grid
                _prev_grid = grid
                row.append(grid)
            self._grids.extend(row)
            _prev_row = row

        for grid in reversed(self._grids):
            grid.update_sprite_cache()

    def get_grid_at(self, x, y):
        i = y // self.grid_height * (self.width // self.grid_height) + (x // self.grid_width)
        if 0 <= i < len(self._grids):
            return self._grids[i]

    def draw(self, camera):
        left, right, bottom, top = camera.scaled_bounds() // 32

        for grid in self._grids:
            far_x = grid.x + grid.width
            far_y = grid.y + grid.height
            if (left <= grid.x <= right or left <= far_x <= right) and \
                    (bottom <= grid.y <= top or bottom <= far_y <= top):
                grid.draw()

    def __setitem__(self, key, value):
        x, y = key
        grid = self.get_grid_at(x, y)
        if grid:
            grid[x, y] = value

            if x > 0 and x % self.grid_width == 0:
                o_grid = self.get_grid_at(x - 1, y)
                o_grid._dirty = True
                if y > 0 and y % self.grid_height == 0:
                    o_grid = self.get_grid_at(x - 1, y - 1)
                    o_grid._dirty = True
            if y > 0 and y % self.grid_height == 0:
                o_grid = self.get_grid_at(x - 1, y - 1)
                o_grid._dirty = True
