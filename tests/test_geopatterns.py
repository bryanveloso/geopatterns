import base64
import xml.etree.ElementTree as ET

import pytest

from geopatterns import GeoPattern

GENERATORS = [
    'bricks',
    'hexagons',
    'overlapping_circles',
    'overlapping_rings',
    'plaid',
    'plus_signs',
    'rings',
    'sinewaves',
    'squares',
    'triangles',
    'xes',
]


@pytest.mark.parametrize('generator', GENERATORS)
def test_generator_produces_valid_svg(generator):
    pattern = GeoPattern('A string for your consideration.', generator=generator)
    root = ET.fromstring(pattern.svg_string)
    assert root.tag == '{http://www.w3.org/2000/svg}svg'
    assert len(root) > 1


@pytest.mark.parametrize('generator', GENERATORS)
def test_same_string_gives_same_svg(generator):
    first = GeoPattern('Mastering markdown', generator=generator)
    second = GeoPattern('Mastering markdown', generator=generator)
    assert first.svg_string == second.svg_string


def test_different_strings_give_different_svg():
    first = GeoPattern('one', generator='squares')
    second = GeoPattern('two', generator='squares')
    assert first.svg_string != second.svg_string


def test_base64_string_decodes_to_svg_string():
    pattern = GeoPattern('A string for your consideration.', generator='xes')
    assert b'\n' not in pattern.base64_string
    assert base64.b64decode(pattern.base64_string).decode() == pattern.svg_string


def test_non_ascii_string():
    pattern = GeoPattern('ünïcödé ✓', generator='squares')
    ET.fromstring(pattern.svg_string)


def test_invalid_generator_raises():
    with pytest.raises(ValueError, match='not a valid generator'):
        GeoPattern('x', generator='nope')
