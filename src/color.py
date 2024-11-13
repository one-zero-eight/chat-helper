from zlib import crc32
import colorsys


def pick_stable_random(to_hash: str):
    hash_value = crc32(to_hash.encode()) & 0xFFFFFFFF
    hue = (hash_value % 100) / 100
    value, saturation = 1, 0.75
    r, g, b = colorsys.hsv_to_rgb(hue, value, saturation)
    r *= 255
    g *= 255
    b *= 255

    return int(r), int(g), int(b)
