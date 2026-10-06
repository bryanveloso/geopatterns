import colorsys
import re

from .utils import promap


def parse_html(html):
    digits = re.findall(r'[0-9a-f]', html, re.IGNORECASE)
    if len(digits) == 3:
        return tuple(int(d * 2, 16) for d in digits)
    if len(digits) == 6:
        return tuple(int(''.join(digits[i:i + 2]), 16) for i in (0, 2, 4))
    raise ValueError('Not a supported HTML colour type.')


def to_svg(rgb):
    return 'rgb({}, {}, {})'.format(*rgb)


def from_color(color):
    return to_svg(parse_html(color))


def from_base_color(base_color, digest):
    hue_offset = promap(int(digest[14:17], 16), 0, 4095, 0, 359)
    sat_offset = int(digest[17], 16)

    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in parse_html(base_color)))

    h = ((h * 360 - hue_offset) / 360) % 1.0

    s = s * 100
    s = s + sat_offset if sat_offset % 2 == 0 else s - sat_offset
    s = min(max(s / 100, 0), 1)

    return to_svg(tuple(round(c * 255) for c in colorsys.hls_to_rgb(h, l, s)))
