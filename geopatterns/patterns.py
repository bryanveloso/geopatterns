import math
from itertools import product

from .utils import promap

DARK = '#222'
LIGHT = '#ddd'
STROKE = '#000'
STROKE_OPACITY = 0.02

# Every pattern takes the SVG to draw on and the digits of the string's hash,
# and returns the size it drew. The registry keeps definition order, which is
# alphabetical, because the hash picks a pattern by index when none is asked for.
PATTERNS = {}


def pattern(func):
    PATTERNS[func.__name__] = func
    return func


def scale(digit, low, high):
    return promap(digit, 0, 15, low, high)


def fill(digit):
    return LIGHT if digit % 2 == 0 else DARK


def opacity(digit):
    return scale(digit, 0.02, 0.15)


def cells(digits):
    """Yield x, y and a hash digit for each cell of the 6x6 grid."""
    for (y, x), digit in zip(product(range(6), repeat=2), digits):
        yield x, y, digit


def tiled(x, y, edge=6):
    """Yield where to draw a cell, then the copies that let the pattern tile."""
    yield x, y
    if x == 0:
        yield edge, y
    if y == 0:
        yield x, edge
    if x == 0 and y == 0:
        yield edge, edge


def plus(svg, size, **attrs):
    with svg.group(**attrs):
        svg.rect(size, 0, size, size * 3)
        svg.rect(0, size, size * 3, size)


@pattern
def chevrons(svg, digits):
    width = height = scale(digits[0], 30, 80)
    e = height * 0.66
    shapes = [
        f'0,0,{width / 2},{height - e},{width / 2},{height},0,{e},0,0',
        f'{width / 2},{height - e},{width},0,{width},{e},{width / 2},{height},{width / 2},{height - e}',
    ]

    for x, y, digit in cells(digits):
        attrs = {
            'stroke': STROKE,
            'stroke_opacity': STROKE_OPACITY,
            'fill': fill(digit),
            'fill_opacity': opacity(digit),
            'stroke_width': 1,
        }
        for row in (y, 6) if y == 0 else (y,):
            with svg.group(**attrs, transform=f'translate({x * width},{row * height * 0.66 - height / 2})'):
                for points in shapes:
                    svg.polyline(points)

    return width * 6, height * 6 * 0.66


@pattern
def concentric_circles(svg, digits):
    ring_size = scale(digits[0], 10, 60)
    stroke_width = ring_size / 5

    for (x, y, digit), outer in zip(cells(digits), digits[::-1][:36]):
        cx = x * ring_size + x * stroke_width + (ring_size + stroke_width) / 2
        cy = y * ring_size + y * stroke_width + (ring_size + stroke_width) / 2

        svg.circle(cx, cy, ring_size / 2, fill='none', stroke=fill(digit), style={
            'opacity': opacity(digit),
            'stroke_width': f'{stroke_width}px',
        })
        svg.circle(cx, cy, ring_size / 4, fill=fill(outer), fill_opacity=opacity(outer))

    size = (ring_size + stroke_width) * 6
    return size, size


@pattern
def diamonds(svg, digits):
    width = scale(digits[0], 10, 50)
    height = scale(digits[1], 10, 50)
    points = f'{width / 2}, 0, {width}, {height / 2}, {width / 2}, {height}, 0, {height / 2}'

    for x, y, digit in cells(digits):
        dx = 0 if y % 2 == 0 else width / 2
        for tx, ty in tiled(x, y):
            svg.polyline(
                points,
                fill=fill(digit),
                fill_opacity=opacity(digit),
                stroke=STROKE,
                stroke_opacity=STROKE_OPACITY,
                transform=f'translate({tx * width - width / 2 + dx}, {height / 2 * ty - height / 2})',
            )

    return width * 6, height * 3


@pattern
def hexagons(svg, digits):
    side = scale(digits[0], 8, 60)
    height = side * math.sqrt(3)
    width = side * 2

    b = math.sin(60 * math.pi / 180) * side
    points = f'0,{b},{side / 2},0,{side / 2 + side},0,{2 * side},{b},{side / 2 + side},{2 * b},{side / 2},{2 * b},0,{b}'

    for x, y, digit in cells(digits):
        dy = y * height if x % 2 == 0 else y * height + height / 2
        positions = [(x, dy - height / 2)]
        if x == 0:
            positions.append((6, dy - height / 2))
        if y == 0:
            dy = 6 * height if x % 2 == 0 else 6 * height + height / 2
            positions.append((x, dy - height / 2))
        if x == 0 and y == 0:
            positions.append((6, 5 * height + height / 2))

        for tx, ty in positions:
            svg.polyline(
                points,
                fill=fill(digit),
                fill_opacity=opacity(digit),
                stroke=STROKE,
                stroke_opacity=STROKE_OPACITY,
                transform=f'translate({tx * side * 1.5 - width / 2}, {ty})',
            )

    return width * 3 + side * 3, height * 6


def mosaic_triangle(svg, points, digit, transforms):
    for transform in transforms:
        svg.polyline(
            points,
            stroke=STROKE,
            stroke_opacity=STROKE_OPACITY,
            fill_opacity=opacity(digit),
            fill=fill(digit),
            transform=transform,
        )


@pattern
def mosaic_squares(svg, digits):
    size = scale(digits[0], 15, 50)
    points = f'0, 0, {size}, {size}, 0, {size}, 0, 0'

    for i, (y, x) in enumerate(product(range(4), repeat=2)):
        left, top = x * size * 2, y * size * 2
        if (x + y) % 2 == 0:
            mosaic_triangle(svg, points, digits[i], [
                f'translate({left}, {top + size}) scale(1, -1)',
                f'translate({left + size * 2}, {top + size}) scale(-1, -1)',
                f'translate({left}, {top + size}) scale(1, 1)',
                f'translate({left + size * 2}, {top + size}) scale(-1, 1)',
            ])
        else:
            mosaic_triangle(svg, points, digits[i], [
                f'translate({left + size}, {top}) scale(-1, 1)',
                f'translate({left + size}, {top + size * 2}) scale(1, -1)',
            ])
            mosaic_triangle(svg, points, digits[i + 1], [
                f'translate({left + size}, {top + size * 2}) scale(-1, -1)',
                f'translate({left + size}, {top}) scale(1, 1)',
            ])

    return size * 8, size * 8


@pattern
def nested_squares(svg, digits):
    block = scale(digits[0], 4, 12)
    square = block * 7

    for (x, y, digit), inner in zip(cells(digits), digits[::-1][:36]):
        svg.rect(
            x * square + x * block * 2 + block / 2,
            y * square + y * block * 2 + block / 2,
            square, square,
            fill='none',
            stroke=fill(digit),
            style={'opacity': opacity(digit), 'stroke_width': f'{block}px'},
        )
        svg.rect(
            x * square + x * block * 2 + block / 2 + block * 2,
            y * square + y * block * 2 + block / 2 + block * 2,
            block * 3, block * 3,
            fill='none',
            stroke=fill(inner),
            style={'opacity': opacity(inner), 'stroke_width': f'{block}px'},
        )

    size = (square + block) * 6 + block * 6
    return size, size


@pattern
def octagons(svg, digits):
    size = scale(digits[0], 10, 60)
    c = size * 0.33
    points = f'{c},0,{size - c},0,{size},{c},{size},{size - c},{size - c},{size},{c},{size},0,{size - c},0,{c},{c},0'

    for x, y, digit in cells(digits):
        svg.polyline(
            points,
            fill=fill(digit),
            fill_opacity=opacity(digit),
            stroke=STROKE,
            stroke_opacity=STROKE_OPACITY,
            transform=f'translate({x * size}, {y * size})',
        )

    return size * 6, size * 6


@pattern
def overlapping_circles(svg, digits):
    radius = scale(digits[0], 25, 200) / 2

    for x, y, digit in cells(digits):
        for tx, ty in tiled(x, y):
            svg.circle(tx * radius, ty * radius, radius, fill=fill(digit), style={'opacity': opacity(digit)})

    return radius * 6, radius * 6


@pattern
def overlapping_rings(svg, digits):
    ring_size = scale(digits[0], 10, 60)
    stroke_width = ring_size / 4

    for x, y, digit in cells(digits):
        for tx, ty in tiled(x, y):
            svg.circle(tx * ring_size, ty * ring_size, ring_size - stroke_width / 2, fill='none', stroke=fill(digit), style={
                'opacity': opacity(digit),
                'stroke_width': f'{stroke_width}px',
            })

    return ring_size * 6, ring_size * 6


@pattern
def plaid(svg, digits):
    stripes = []
    position = 0
    for space, digit in zip(digits[0:36:2], digits[1:36:2]):
        position += space + 5
        stripes.append((position, digit + 5, digit))
        position += digit + 5

    # The same stripes run both ways, so the pattern is square.
    for offset, size, digit in stripes:
        svg.rect(0, offset, '100%', size, opacity=opacity(digit), fill=fill(digit))
    for offset, size, digit in stripes:
        svg.rect(offset, 0, size, '100%', opacity=opacity(digit), fill=fill(digit))

    return position, position


@pattern
def plus_signs(svg, digits):
    square = scale(digits[0], 10, 25)
    size = square * 3

    for x, y, digit in cells(digits):
        dx = 0 if y % 2 == 0 else 1
        for tx, ty in tiled(x, y, edge=4):
            plus(
                svg, square,
                fill=fill(digit),
                stroke=STROKE,
                stroke_opacity=STROKE_OPACITY,
                style={'fill_opacity': opacity(digit)},
                transform=f'translate({tx * size - x * square + dx * square - square},{ty * size - y * square - size / 2})',
            )

    return square * 12, square * 12


@pattern
def sine_waves(svg, digits):
    period = math.floor(scale(digits[0], 100, 400))
    amplitude = math.floor(scale(digits[1], 30, 100))
    wave_width = math.floor(scale(digits[2], 3, 30))

    x_offset = period // 4 * 0.7
    wave = (
        f'M0 {amplitude} C {x_offset} 0, {period // 2 - x_offset} 0, {period // 2} {amplitude} '
        f'S {period - x_offset} {amplitude * 2}, {period} {amplitude} '
        f'S {period * 1.5 - x_offset} 0, {period * 1.5}, {amplitude}'
    )

    for i, digit in enumerate(digits[:36]):
        attrs = {
            'fill': 'none',
            'stroke': fill(digit),
            'style': {'opacity': opacity(digit), 'stroke_width': f'{wave_width}px'},
        }
        top = wave_width * i - amplitude * 1.5
        svg.path(wave, **attrs, transform=f'translate(-{period // 4}, {top})')
        svg.path(wave, **attrs, transform=f'translate(-{period // 4}, {top + wave_width * 36})')

    return period, wave_width * 36


@pattern
def squares(svg, digits):
    size = scale(digits[0], 10, 60)

    for x, y, digit in cells(digits):
        svg.rect(
            x * size, y * size, size, size,
            fill=fill(digit),
            fill_opacity=opacity(digit),
            stroke=STROKE,
            stroke_opacity=STROKE_OPACITY,
        )

    return size * 6, size * 6


@pattern
def tessellation(svg, digits):
    # 3.4.6.4 semi-regular tessellation
    side = scale(digits[0], 5, 40)
    hex_height = side * math.sqrt(3)
    hex_width = side * 2
    triangle_height = side / 2 * math.sqrt(3)
    triangle = f'0, 0, {triangle_height}, {side / 2}, 0, {side}, 0, 0'
    width = side * 3 + triangle_height * 2
    height = (hex_height * 2) + (side * 2)

    for i, digit in enumerate(digits[:20]):
        attrs = {
            'stroke': STROKE,
            'stroke_opacity': STROKE_OPACITY,
            'fill': fill(digit),
            'fill_opacity': opacity(digit),
            'stroke_width': 1,
        }

        def square(x, y, transform=None):
            extra = {'transform': transform} if transform else {}
            svg.rect(x, y, side, side, **attrs, **extra)

        def tri(transform):
            svg.polyline(triangle, **attrs, transform=transform)

        match i:
            case 0:  # all 4 corners
                square(-side / 2, -side / 2)
                square(width - side / 2, -side / 2)
                square(-side / 2, height - side / 2)
                square(width - side / 2, height - side / 2)
            case 1:  # center / top square
                square(hex_width / 2 + triangle_height, hex_height / 2)
            case 2:  # side squares
                square(-side / 2, height / 2 - side / 2)
                square(width - side / 2, height / 2 - side / 2)
            case 3:  # center / bottom square
                square(hex_width / 2 + triangle_height, hex_height * 1.5 + side)
            case 4:  # left top / bottom triangle
                tri(f'translate({side / 2}, {-side / 2}) rotate(0, {side / 2}, {triangle_height / 2})')
                tri(f'translate({side / 2}, {height - -side / 2}) rotate(0, {side / 2}, {triangle_height / 2}) scale(1, -1)')
            case 5:  # right top / bottom triangle
                tri(f'translate({width - side / 2}, {-side / 2}) rotate(0, {side / 2}, {triangle_height / 2}) scale(-1, 1)')
                tri(f'translate({width - side / 2}, {height + side / 2}) rotate(0, {side / 2}, {triangle_height / 2}) scale(-1, -1)')
            case 6:  # center / top / right triangle
                tri(f'translate({width / 2 + side / 2}, {hex_height / 2})')
            case 7:  # center / top / left triangle
                tri(f'translate({width - width / 2 - side / 2}, {hex_height / 2}) scale(-1, 1)')
            case 8:  # center / bottom / right triangle
                tri(f'translate({width / 2 + side / 2}, {height - hex_height / 2}) scale(1, -1)')
            case 9:  # center / bottom / left triangle
                tri(f'translate({width - width / 2 - side / 2}, {height - hex_height / 2}) scale(-1, -1)')
            case 10:  # left / middle triangle
                tri(f'translate({side / 2}, {height / 2 - side / 2})')
            case 11:  # right / middle triangle
                tri(f'translate({width - side / 2}, {height / 2 - side / 2}) scale(-1, 1)')
            case 12:  # left / top square
                square(0, 0, f'translate({side / 2}, {side / 2}) rotate(-30, 0, 0)')
            case 13:  # right / top square
                square(0, 0, f'scale(-1, 1) translate({-width + side / 2}, {side / 2}) rotate(-30, 0, 0)')
            case 14:  # left / center-top square
                square(0, 0, f'translate({side / 2}, {height / 2 - side / 2 - side}) rotate(30, 0, {side})')
            case 15:  # right / center-top square
                square(0, 0, f'scale(-1, 1) translate({-width + side / 2}, {height / 2 - side / 2 - side}) rotate(30, 0, {side})')
            case 16:  # left / center-bottom square
                square(0, 0, f'scale(1, -1) translate({side / 2}, {-height + height / 2 - side / 2 - side}) rotate(30, 0, {side})')
            case 17:  # right / center-bottom square
                square(0, 0, f'scale(-1, -1) translate({-width + side / 2}, {-height + height / 2 - side / 2 - side}) rotate(30, 0, {side})')
            case 18:  # left / bottom square
                square(0, 0, f'scale(1, -1) translate({side / 2}, {-height + side / 2}) rotate(-30, 0, 0)')
            case 19:  # right / bottom square
                square(0, 0, f'scale(-1, -1) translate({-width + side / 2}, {-height + side / 2}) rotate(-30, 0, 0)')

    return width, height


@pattern
def triangles(svg, digits):
    side = scale(digits[0], 15, 80)
    height = side / 2 * math.sqrt(3)
    points = f'{side / 2}, 0, {side}, {height}, 0, {height}, {side / 2}, 0'

    for x, y, digit in cells(digits):
        flipped = (x + y) % 2 == 0
        rotation = 180 if flipped else 0
        for tx in (x, 6) if x == 0 else (x,):
            svg.polyline(
                points,
                fill=fill(digit),
                fill_opacity=opacity(digit),
                stroke=STROKE,
                stroke_opacity=STROKE_OPACITY,
                transform=f'translate({tx * side * 0.5 - side / 2}, {height * y}) rotate({rotation}, {side / 2}, {height / 2})',
            )

    return side * 3, height * 6


@pattern
def xes(svg, digits):
    square = scale(digits[0], 10, 25)
    size = square * 3 * 0.943

    for x, y, digit in cells(digits):
        def dy(row):
            return row * size - size * 0.5 + (size / 4 if x % 2 else 0)

        # Column, vertical offset and row for each copy, the last two for tiling.
        copies = [(x, dy(y), y)]
        if x == 0:
            copies.append((6, dy(y), y))
        if y == 0:
            copies.append((x, dy(6), 6))
        if y == 5:
            copies.append((x, dy(5), 11))
        if x == 0 and y == 0:
            copies.append((6, dy(6), 6))

        for column, offset, row in copies:
            plus(
                svg, square,
                fill=fill(digit),
                style={'opacity': opacity(digit)},
                transform=f'translate({column * size / 2 - size / 2},{offset - row * size / 2}) rotate(45, {size / 2}, {size / 2})',
            )

    return size * 3, size * 3
