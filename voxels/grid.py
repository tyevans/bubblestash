from collections import Counter

import numpy as np
import pyglet

from voxels.voxel import EMPTY_VOXEL, Voxel


class VoxelGrid(object):

    def __init__(self, x, y, width, height, space, state=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.space = space
        self.state = state if state is not None else (np.ones(self.width, self.height, 3) * EMPTY_VOXEL)
        self._sprite_batch = pyglet.graphics.Batch()
        self._sprite_cache = []
        self._dirty = True

    def get_state_at(self, x, y):
        _x = x - self.x
        _y = y - self.y
        if _x < 0 or _y < 0:
            return EMPTY_VOXEL
        elif _x >= self.width:
            if hasattr(self, 'neighbor_x') and self.neighbor_x is not None:
                return self.neighbor_x.get_state_at(x, y)
            else:
                return EMPTY_VOXEL
        elif _y >= self.height:
            if hasattr(self, 'neighbor_y') and self.neighbor_y is not None:
                return self.neighbor_y.get_state_at(x, y)
            else:
                return EMPTY_VOXEL
        else:
            s_height, s_width = self.state.shape[:2]
            if s_height > _y and s_width > _x:
                return tuple(self.state[_y, _x].tolist())
            else:
                return EMPTY_VOXEL

    def update_sprite_cache(self):
        self._dirty = False
        height, width = self.state.shape[:2]
        for instances in self._sprite_cache:
            for inst in instances:
                self.space.remove(inst.body, inst.shape)
                inst.delete()
        _new_cache = []
        for y in range(self.y, height + self.y):
            for x in range(self.x, width + self.x):
                cell_weights = [
                    (1, (x, y)),
                    (2, (x + 1, y)),
                    (4, (x + 1, y + 1)),
                    (8, (x, y + 1))
                ]

                shape_values = Counter()
                for weight, pos in cell_weights:
                    value = self.get_state_at(*pos)
                    if value != EMPTY_VOXEL:
                        shape_values[value] += weight
                total = sum(shape_values.values())
                instances = []
                for value, weight in sorted(shape_values.items(), reverse=True):
                    inst = Voxel.by_color(value, x=x, y=y, value=value, shape_value=total, batch=self._sprite_batch)
                    self.space.add(inst.body, inst.shape)
                    total -= weight
                    if inst:
                        instances.append(inst)
                _new_cache.append(instances)
        self._sprite_cache = _new_cache

    def __setitem__(self, key, value):
        self._dirty = True
        x, y = key
        _x = x - self.x
        _y = y - self.y
        self.state[_y, _x] = value

    def draw(self):
        if self._dirty:
            self.update_sprite_cache()
        self._sprite_batch.draw()
