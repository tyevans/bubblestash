import random
from operator import itemgetter

import cv2
import numpy as np

from voxels.voxel import EMPTY_VOXEL


def perlin(x, y, seed=0):
    # permutation table
    np.random.seed(seed)
    p = np.arange(256, dtype=int)
    np.random.shuffle(p)
    p = np.stack([p, p]).flatten()
    # coordinates of the top-left
    xi = x.astype(int)
    yi = y.astype(int)
    # internal coordinates
    xf = x - xi
    yf = y - yi
    # fade factors
    u = fade(xf)
    v = fade(yf)
    # noise components
    n00 = gradient(p[p[xi] + yi], xf, yf)
    n01 = gradient(p[p[xi] + yi + 1], xf, yf - 1)
    n11 = gradient(p[p[xi + 1] + yi + 1], xf - 1, yf - 1)
    n10 = gradient(p[p[xi + 1] + yi], xf - 1, yf)
    # combine noises
    x1 = lerp(n00, n10, u)
    x2 = lerp(n01, n11, u)  # FIX1: I was using n10 instead of n01
    return lerp(x1, x2, v)  # FIX2: I also had to reverse x1 and x2 here


def lerp(a, b, x):
    "linear interpolation"
    return a + x * (b - a)


def fade(t):
    "6t^5 - 15t^4 + 10t^3"
    return 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3


def gradient(h, x, y):
    "grad converts h to the right gradient vector and return the dot product with (x,y)"
    vectors = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
    g = vectors[h % 4]
    return g[:, :, 0] * x + g[:, :, 1] * y


def generate_random_map(width, height, voxels, base_voxel=None):
    map_img = np.ones((width, height, 3))
    if base_voxel and base_voxel != EMPTY_VOXEL:
        map_img *= base_voxel.color
    else:
        map_img *= EMPTY_VOXEL

    for voxel_cls, scarcity in sorted(voxels.items(), key=itemgetter(1), reverse=True):
        lin_w = np.linspace(0, 5, width, endpoint=False)
        lin_h = np.linspace(0, 5, height, endpoint=False)
        x, y = np.meshgrid(lin_w, lin_h)
        img = (perlin(x, y, seed=random.randint(0, 2 ** 32 - 1)) * 255).astype(np.uint8)
        ret, thresh = cv2.threshold(img, 255 - 255 * scarcity, 255, cv2.THRESH_BINARY)
        map_img[thresh == 255] = voxel_cls.color

    # lin_w = np.linspace(0, 5, width, endpoint=False)
    # lin_h = np.linspace(0, 5, height, endpoint=False)
    # x, y = np.meshgrid(lin_w, lin_h)
    # img = (perlin(x, y, seed=random.randint(0, 2 ** 32 - 1)) * 255).astype(np.uint8)
    # ret, thresh = cv2.threshold(img, 0.1, 240, cv2.THRESH_BINARY_INV)
    # cv2.imshow("frame", img)
    # cv2.imshow("thresh", thresh)
    # cv2.waitKey(0)
    # map_img[thresh == 255] = EMPTY_VOXEL

    return map_img
