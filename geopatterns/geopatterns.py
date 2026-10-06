import base64
import hashlib
import warnings

from .color import from_base_color, from_color
from .patterns import PATTERNS
from .svg import SVG

DEFAULT_BASE_COLOR = '#933c3c'

# Generators this library had before it caught up with upstream, and what
# upstream replaced them with.
LEGACY_GENERATORS = {
    'bricks': 'octagons',
    'rings': 'concentric_circles',
    'sinewaves': 'sine_waves',
}


class InvalidPatternError(ValueError):
    pass


def requested_patterns(patterns, generator):
    requested = [patterns] if isinstance(patterns, str) else list(patterns or [])

    if generator is not None:
        warnings.warn('The generator argument is deprecated, use patterns instead.', DeprecationWarning, stacklevel=3)
        names = [generator] if isinstance(generator, str) else list(generator)
        for name in names:
            if name in LEGACY_GENERATORS:
                warnings.warn(
                    f'{name!r} is deprecated and draws {LEGACY_GENERATORS[name]!r} now, use patterns={LEGACY_GENERATORS[name]!r}.',
                    DeprecationWarning,
                    stacklevel=3,
                )
        requested = [LEGACY_GENERATORS.get(name, name) for name in names] + requested

    return list(dict.fromkeys(requested))


class GeoPattern:
    def __init__(self, string, patterns=None, color=None, base_color=None, generator=None):
        requested = requested_patterns(patterns, generator)
        unknown = [name for name in requested if name not in PATTERNS]
        if unknown:
            raise InvalidPatternError(f'Error: At least one of the requested patterns "{", ".join(requested)}" is invalid')

        self.hash = hashlib.sha1(string.encode('utf8')).hexdigest()
        digits = [int(char, 16) for char in self.hash]

        available = requested or list(PATTERNS)
        name = available[min(digits[20], len(available) - 1)]

        if color:
            background = from_color(color)
        else:
            background = from_base_color(base_color or DEFAULT_BASE_COLOR, self.hash)

        self.svg = SVG()
        self.svg.rect(0, 0, '100%', '100%', fill=background)
        self.svg.width, self.svg.height = PATTERNS[name](self.svg, digits)

    @property
    def svg_string(self):
        return str(self.svg)

    @property
    def base64_string(self):
        return base64.b64encode(str(self.svg).encode())
