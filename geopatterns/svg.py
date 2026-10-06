import math
from contextlib import contextmanager


def attributes(attrs):
    parts = []
    for name, value in attrs.items():
        if isinstance(value, dict):
            value = ''.join(f'{key.replace("_", "-")}:{val};' for key, val in value.items())
        parts.append(f'{name.replace("_", "-")}="{value}" ')
    return ''.join(parts)


class SVG:
    def __init__(self, width=100, height=100):
        self.width = width
        self.height = height
        self.elements = []

    def __str__(self):
        header = f'<svg xmlns="http://www.w3.org/2000/svg" width="{math.floor(self.width)}" height="{math.floor(self.height)}">'
        return header + ''.join(self.elements) + '</svg>'

    def rect(self, x, y, width, height, **attrs):
        self.elements.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" {attributes(attrs)} />')

    def circle(self, cx, cy, r, **attrs):
        self.elements.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" {attributes(attrs)} />')

    def path(self, d, **attrs):
        self.elements.append(f'<path d="{d}" {attributes(attrs)} />')

    def polyline(self, points, **attrs):
        self.elements.append(f'<polyline points="{points}" {attributes(attrs)} />')

    @contextmanager
    def group(self, **attrs):
        self.elements.append(f'<g {attributes(attrs)}>')
        yield
        self.elements.append('</g>')
