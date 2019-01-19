import numpy as np
import pyglet

EMPTY_VOXEL = (255, 255, 255)


class Voxel(pyglet.sprite.Sprite):
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
        super().__init__(img=self._voxels_sequence[self.shape_value], x=x * 32, y=y * 32, **kwargs)

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
