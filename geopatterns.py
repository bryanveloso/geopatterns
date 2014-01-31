# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import hashlib
import math

from colour import Color


class SVG(object):
    def __init__(self):
        self.width = 100
        self.height = 100
        self.svg_string = ''

    @property
    def svg_header(self):
        return '<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'.format(**{
            'width': self.width, 'height': self.height
        })

    @property
    def svg_closer(self):
        return '</svg>'

    def to_string(self):
        return ''.join([self.svg_header, self.svg_string, self.svg_closer])

    def rect(self, x, y, width, height, **kwargs):
        self.svg_string += '<rect x="{x}" y="{y}" width="{width}" height="{height}" {kwargs}/>'.format(**{
            'x': x, 'y': y, 'width': width, 'height': height, 'kwargs': self.write_args(**kwargs)
        })

    def circle(self, cx, cy, r, **kwargs):
        self.svg_string += '<circle cx="{cx}" cy="{cy}" r="{r}" {kwargs}/>'.format(**{
            'cx': cx, 'cy': cy, 'r': r, 'kwargs': self.write_args(**kwargs)
        })

    def path(self, str, **kwargs):
        self.svg_string += '<path d="{str}" {kwargs}/>'.format(**{
            'str': str, 'kwargs': self.write_args(**kwargs)
        })

    def polyline(self, str, **kwargs):
        self.svg_string += '<polyline points="{str}" {kwargs}/>'.format(**{
            'str': str, 'kwargs': self.write_args(**kwargs)
        })

    def group(self, elements, **kwargs):
        self.svg_string += '<g {kwargs}>'.format({'kwargs': self.write_args(**kwargs)})
        (eval(element) for element in elements)
        self.svg_string += '</g>'

    def write_args(self, **kwargs):
        str = ''
        for key, value in kwargs.iteritems():
            if isinstance(value, dict):
                str += '{}="'.format(key)
                for key, value in value.iteritems():
                    str += '{}:{};'.format(key, value)
                str += '" '
            else:
                str += '{}="{}" '.format(key, value)
        return str


# Python implementation of Processing's map function
# http://processing.org/reference/map_.html
def promap(value, v_min, v_max, d_min, d_max):  # v for value, d for desired
    v_value = float(value)
    v_range = v_max - v_min
    d_range = d_max - d_min
    d_value = (v_value - v_min) * d_range / v_range + d_min
    return d_value


class GeoPattern(object):
    def __init__(self, string):
        self.hash = hashlib.sha1(string).hexdigest()
        self.svg = SVG()

        self.generate_background()
        self.geoHexagons()

    def svg_string(self):
        return self.svg.to_string()

    def base64_string(self):
        return base64.encode(self.svg.to_string())

    def generate_background(self):
        hue_offset = promap(int(self.hash[14:][:3], 16), 0, 4095, 0, 359)
        sat_offset = int(self.hash[17:][:1], 16)
        base_color = Color(hsl=(0, .42, .41))
        base_color.hue = base_color.hue - hue_offset

        if sat_offset % 2:
            base_color.saturation = base_color.saturation + sat_offset / 100
        else:
            base_color.saturation = base_color.saturation - sat_offset / 100

        rgb = base_color.rgb
        r = round(rgb[0] * 255)
        g = round(rgb[1] * 255)
        b = round(rgb[2] * 255)
        return self.svg.rect(0, 0, '100%', '100%', **{
            'fill': 'rgb({}, {}, {})'.format(r, g, b)
        })

    def geo_hexagons(self):
        scale = int(self.hash[1:][:1], 16)
        side_length = promap(scale, 0, 15, 5, 120)
        hex_height = side_length * math.sqrt(3)
        hex_width = side_length * 2
        hex = self.build_hexagon_shape(side_length)

        self.svg.width = (hex_width * 3) + (side_length * 3)
        self.svg.height = hex_height * 6

        i = 0
        for y in range(5):
            for x in range(5):
                val = int(self.hash[i:][:1], 16)
                dy = (y * hex_height) if x % 2 else (y * hex_height + hex_height / 2)
                opacity = promap(val, 0, 15, 0.02, 0.18)
                fill = '#ddd' if val % 2 == 0 else '#222'
                tmp_hex = str(hex)

                self.svg.polyline(hex, **{
                    'opacity': opacity,
                    'fill': fill,
                    'stroke': '#000000',
                    'transform': 'translate({}, {})'.format(
                        x * side_length * 1.5 - hex_width / 2,
                        dy - hex_height / 2
                    )
                })

                # Add an extra one at top-right, for tiling.
                if x == 0:
                    self.svg.polyline(hex, **{
                        'opacity': opacity,
                        'fill': fill,
                        'stroke': '#000000',
                        'transform': 'translate({}, {})'.format(
                            6 * side_length * 1.5 - hex_width / 2,
                            dy - hex_height / 2
                        )
                    })

                # Add an extra row at the end that matches the first row, for tiling.
                if y == 0:
                    dy = (6 * hex_height) if x % 2 == 0 else (6 * hex_height + hex_height / 2)
                    self.svg.polyline(hex, **{
                        'opacity': opacity,
                        'fill': fill,
                        'stroke': '#000000',
                        'transform': 'translate({}, {})'.format(
                            x * side_length * 1.5 - hex_width / 2,
                            dy - hex_height / 2
                        )
                    })

                # Add an extra one at bottom-right, for tiling.
                if x == 0 and y == 0:
                    self.svg.polyline(hex, **{
                        'opacity': opacity,
                        'fill': fill,
                        'stroke': '#000000',
                        'transform': 'translate({}, {})'.format(
                            6 * side_length * 1.5 - hex_width / 2,
                            5 * hex_height + hex_height / 2
                        )
                    })

                i += 1

    def geo_sinewaves(self):
        period = math.floor(promap(int(self.hash[1:][:1], 16), 0, 15, 100, 400))
        amplitude = math.floor(promap(int(self.hash[2:][:1], 16), 0, 15, 30, 100))
        wave_width = math.floor(promap(int(self.hash[3:][:1], 16), 0, 15, 3, 30))

        self.svg.width = period
        self.svg.height = wave_width * 36

        for i in range(35):
            val = int(self.hash[i:][1], 16)
            fill = '#ddd' if val % 2 == 0 else '#222'
            opacity = promap(val, 0, 15, 0.02, 0.15)
            x_offset = period / 4 * 0.7

            str = 'M0 {} C {} 0, {} 0, {} {} S {} {}, {} {} S {} 0, {}, {}'.format(
                amplitude, x_offset, (period / 2 - x_offset), (period / 2),
                amplitude, (period - x_offset), (amplitude * 2), period,
                amplitude, (period * 1.5 - x_offset), (period * 1.5), amplitude
            )

            self.svg.path(str, **{
                'fill': 'none',
                'stroke': fill,
                'transform': 'translate({}, {})'.format(
                    (period / 4), (wave_width * i - amplitude * 1.5)
                ),
                'style': {
                    'opacity': opacity,
                    'stroke_width': '{}px'.format(wave_width)
                }
            })

            self.svg.path(str, **{
                'fill': 'none',
                'stroke': fill,
                'transform': 'translate({}, {})'.format(
                    (period / 4), (wave_width * i - amplitude * 1.5 + wave_width * 36)
                ),
                'style': {
                    'opacity': opacity,
                    'stroke_width': '{}px'.format(wave_width)
                }
            })

    def build_hexagon_shape(self, side_length):
        c = side_length
        a = c / 2
        b = math.sin(60 * math.pi / 180) * c
        return '0, {}, {}, 0, {}, 0, {}, {}, {}, {}, {}, {}, 0, {}'.format(
            b, a, a + c, 2 * c, b, a + c, 2 * b, a, 2 * b, b
        )
