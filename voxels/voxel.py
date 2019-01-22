import numpy as np
import pyglet
import pymunk

from bubblestash.actor import Actor

EMPTY_VOXEL = (255, 255, 255)


class Voxel(Actor):
    _voxels_by_color = {}
    color = None
    voxels_image_path = None

    def __init__(self, x, y, value=0, shape_value=0, **kwargs):
        if not hasattr(self.__class__, '_voxels_sequence'):
            self.__class__._voxels_image = pyglet.resource.image(self.voxels_image_path)
            self.__class__._voxels_sequence = pyglet.image.ImageGrid(
                self.__class__._voxels_image, 1, 16)

        self.value = value
        self.shape_value = shape_value

        body = pymunk.Body(body_type=pymunk.Body.STATIC, moment=10000)

        if shape_value == 1:
            vertices = [
                (0, 0),
                (16, 0),
                (0, 16),
            ]
        elif shape_value == 2:
            vertices = [
                (16, 0),
                (32, 0),
                (32, 16),
            ]
        elif shape_value == 3:
            vertices = [
                (0, 0),
                (32, 0),
                (32, 16),
                (0, 16),
            ]
        elif shape_value == 4:
            vertices = [
                (16, 32),
                (32, 16),
                (32, 32),
            ]
        elif shape_value == 5:
            vertices = [
                (0, 0),
                (16, 0),
                (32, 16),
                (32, 32),
                (16, 32),
                (0, 16)
            ]
        elif shape_value == 6:
            vertices = [
                (16, 0),
                (32, 0),
                (32, 32),
                (16, 32)
            ]
        elif shape_value == 7:
            vertices = [
                (0, 0),
                (32, 0),
                (32, 32),
                (16, 32),
                (0, 16),
            ]
        elif shape_value == 8:
            vertices = [
                (0, 32),
                (0, 16),
                (16, 32)
            ]
        elif shape_value == 9:
            vertices = [
                (0, 0),
                (16, 0),
                (16, 32),
                (0, 32)
            ]
        elif shape_value == 10:
            vertices = [
                (0, 16),
                (16, 0),
                (32, 0),
                (32, 16),
                (16, 32),
                (0, 32)
            ]
        elif shape_value == 11:
            vertices = [
                (0, 0),
                (32, 0),
                (32, 16),
                (16, 32),
                (0, 32)
            ]
        elif shape_value == 12:
            vertices = [
                (0, 16),
                (32, 16),
                (32, 32),
                (0, 32)
            ]
        elif shape_value == 13:
            vertices = [
                (0, 0),
                (16, 0),
                (32, 16),
                (32, 32),
                (0, 32)
            ]
        elif shape_value == 14:
            vertices = [
                (16, 0),
                (32, 0),
                (32, 32),
                (0, 32),
                (0, 16)
            ]
        elif shape_value == 15:
            vertices = [
                (0, 0),
                (32, 0),
                (32, 32),
                (0, 32)
            ]
        else:
            vertices = []

        poly = pymunk.Poly(body, vertices=vertices)
        poly.elasticity = .2
        poly.friction = 0.85
        super().__init__(body=body, shape=poly, img=self._voxels_sequence[self.shape_value], x=x * 32, y=y * 32,
                         **kwargs)

    @classmethod
    def by_color(cls, color, x, y, value=0, shape_value=0, **kwargs):
        if isinstance(color, np.ndarray):
            color = tuple(color.tolist())
        _cls = cls._voxels_by_color.get(color)
        if not _cls:
            cls._voxels_by_color.update({cls.color: cls for cls in cls.__subclasses__()})
            _cls = cls._voxels_by_color.get(color)
        if _cls:
            return _cls(x, y, value=value, shape_value=shape_value, **kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__} x={self.x} y={self.y} shape_value={self.shape_value}>"


class DirtVoxel(Voxel):
    color = (0, 0, 0)
    voxels_image_path = "data/images/voxels/dirt.png"


class MarbleVoxel(Voxel):
    color = (18, 56, 94)
    voxels_image_path = "data/images/voxels/marble.png"


class IronVoxel(Voxel):
    color = (128, 128, 128)
    voxels_image_path = "data/images/voxels/iron.png"


class DiamondVoxel(Voxel):
    color = (128, 128, 100)
    voxels_image_path = "data/images/voxels/diamond.png"
