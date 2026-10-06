GeoPatterns
===========

![The xes pattern, tiled.](https://raw.githubusercontent.com/bryanveloso/geopatterns/main/docs/example.png)

Generate beautiful SVG patterns from a string. This is a Python-port of
[Jason Long][1]'s [Ruby library][2].

[1]: https://github.com/jasonlong/
[2]: https://github.com/jasonlong/geo_pattern/

Installation
------------

GeoPatterns requires Python 3.11 or newer and is installable via `pip`:

```shell
$ pip install geopatterns
```

Usage
-----

Create a new pattern by initializing `GeoPattern()` with a string. The string
is hashed, and the hash decides the pattern, the background color and the size
of the shapes.

```python
>>> from geopatterns import GeoPattern
>>> pattern = GeoPattern('A string for your consideration.')
```

To use a specific pattern, or a subset of the available patterns:

```python
>>> GeoPattern('A string for your consideration.', patterns='sine_waves')
>>> GeoPattern('A string for your consideration.', patterns=['sine_waves', 'xes'])
```

To pick a base color (its hue and saturation still shift with the string), or
to use an exact color:

```python
>>> GeoPattern('A string for your consideration.', base_color='#fc0')
>>> GeoPattern('A string for your consideration.', color='#fc0')
```

Available patterns are:

* `chevrons`
* `concentric_circles`
* `diamonds`
* `hexagons`
* `mosaic_squares`
* `nested_squares`
* `octagons`
* `overlapping_circles`
* `overlapping_rings`
* `plaid`
* `plus_signs`
* `sine_waves`
* `squares`
* `tessellation`
* `triangles`
* `xes`

`generator=` still works but is deprecated, use `patterns=`. The old `bricks`,
`rings` and `sinewaves` generators are gone. Upstream replaced them with
`octagons`, `concentric_circles` and `sine_waves`, and passing the old names to
`generator=` draws those instead, with a warning.

Get the SVG string:

```python
>>> print(pattern.svg_string)
<svg xmlns="http://www.w3.org/2000/svg" ...
```

Get the Base64-encoded string (as `bytes`):

```python
>>> print(pattern.base64_string)
b'PHN2ZyB4bWxucz0iaHR0cDov...
```

In the case of the Base64-encoded string, you can use it in CSS as follows:

```css
body {
  background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz...zdmc+');
}
```

You can use `cairosvg` to save the SVG string as a PNG image. First, install `cairosvg`:

```
pip install cairosvg
```

And then run:

```python
>>> import cairosvg
>>> from geopatterns import GeoPattern
>>> pattern = GeoPattern('A string for your consideration.', patterns='xes')
>>> cairosvg.svg2png(bytestring=pattern.svg_string, write_to="output.png")
```

If you just want to visualize the pattern, you can use `cairosvg` with `PIL`:

```python
>>> from io import BytesIO
>>> import matplotlib.pyplot as plt
>>> from PIL import Image
>>> import cairosvg
>>> from geopatterns import GeoPattern
>>> pattern = GeoPattern('A string for your consideration.', patterns='xes')
>>> png = cairosvg.svg2png(bytestring=pattern.svg_string)
>>> image = Image.open(BytesIO(png))
>>> plt.imshow(image)
>>> plt.show()
```

Compatibility
-------------

For the same string and options, the SVG matches what [geo_pattern][2] 1.5.0
produces. The tests check this against upstream's fixtures and against hashes
generated from its Ruby code.

Development
-----------

```shell
$ uv run pytest
```

`tests/fixtures/hashes.json` comes from upstream. To regenerate it, check out
[geo_pattern][2], install its `color` gem, and run:

```shell
$ ruby -I<upstream>/lib tests/ruby/generate_hashes.rb <upstream> > tests/fixtures/hashes.json
```
