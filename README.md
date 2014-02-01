GeoPatterns
===========

![](https://f.cloud.github.com/assets/1258/2056725/ede0785e-8aea-11e3-9e1e-45931b6e1c83.png)

Generate beautiful SVG patterns from a string. This is a Python-port of
[Jason Long][1]'s [Ruby library][2].

[1]: https://github.com/jasonlong/
[2]: https://github.com/jasonlong/geopatterns/

Installation
------------

GeoPatterns is installable via `pip`:

```shell
$ pip install geopatterns
```

Usage
-----

Create a new pattern by initializing `GeoPattern()` with a string and a
generator (the result of this string/generator pair is the above image).

```python
>>> from geopatterns import GeoPattern
>>> pattern = GeoPattern('A string for your consideration.', generator='xes')
```

Currently available generators are:

* `hexagons`
* `overlappingcircles`
* `rings`
* `sinewaves`
* `squares`
* `xes`

Get the SVG string:

```python
>>> print(pattern.svg_string)
u'<svg xmlns="http://www.w3.org/2000/svg" ...
```

Get the Base64-encoded string:

```python
>>> print(pattern.base64_string)
'PHN2ZyB4bWxucz0iaHR0cDov...
```

In the case of the Base64-encoded string, you can use it in CSS as follows:

```css
body {
  background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz...zdmc+');
}
```
