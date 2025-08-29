import colorsys
from zlib import crc32


def pick_stable_random(to_hash: str):
    hash_value = crc32(to_hash.encode()) & 0xFFFFFFFF
    hue = (hash_value % 360) / 360
    saturation, value = 0.75, 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    r *= 255
    g *= 255
    b *= 255

    return int(r), int(g), int(b)
