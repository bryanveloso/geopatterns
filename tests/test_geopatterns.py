import base64
import xml.etree.ElementTree as ET

import pytest

from geopatterns import GeoPattern, InvalidPatternError
from geopatterns.patterns import PATTERNS


@pytest.mark.parametrize('pattern', PATTERNS)
def test_generator_produces_valid_svg(pattern):
    svg = GeoPattern('A string for your consideration.', patterns=pattern)
    root = ET.fromstring(svg.svg_string)
    assert root.tag == '{http://www.w3.org/2000/svg}svg'
    assert len(root) > 1


@pytest.mark.parametrize('pattern', PATTERNS)
def test_same_string_gives_same_svg(pattern):
    first = GeoPattern('A string for your consideration.', patterns=pattern)
    second = GeoPattern('A string for your consideration.', patterns=pattern)
    assert first.svg_string == second.svg_string


def test_different_strings_give_different_svg():
    first = GeoPattern('one', patterns='squares')
    second = GeoPattern('two', patterns='squares')
    assert first.svg_string != second.svg_string


def test_base64_string_decodes_to_svg_string():
    pattern = GeoPattern('A string for your consideration.', patterns='squares')
    assert b'\n' not in pattern.base64_string
    assert base64.b64decode(pattern.base64_string).decode() == pattern.svg_string


def test_non_ascii_string():
    pattern = GeoPattern('ünïcödé ✓', patterns='squares')
    ET.fromstring(pattern.svg_string)


def test_patterns_accepts_a_string_or_a_list():
    assert GeoPattern('x', patterns='squares').svg_string == GeoPattern('x', patterns=['squares']).svg_string


def test_color_sets_the_background():
    svg = GeoPattern('x', patterns='squares', color='#00ff00').svg_string
    assert 'fill="rgb(0, 255, 0)"' in svg


def test_invalid_pattern_raises():
    with pytest.raises(InvalidPatternError, match='is invalid'):
        GeoPattern('x', patterns='nope')


def test_invalid_pattern_is_a_value_error():
    with pytest.raises(ValueError):
        GeoPattern('x', patterns='nope')


def test_invalid_color_raises():
    with pytest.raises(ValueError, match='HTML colour'):
        GeoPattern('x', patterns='squares', color='nope')


def test_generator_is_deprecated():
    with pytest.warns(DeprecationWarning, match='patterns'):
        deprecated = GeoPattern('x', generator='squares')
    assert deprecated.svg_string == GeoPattern('x', patterns='squares').svg_string


@pytest.mark.parametrize('legacy, current', [
    ('bricks', 'octagons'),
    ('rings', 'concentric_circles'),
    ('sinewaves', 'sine_waves'),
])
def test_legacy_generator_names_point_at_their_replacement(legacy, current):
    with pytest.warns(DeprecationWarning) as warnings:
        deprecated = GeoPattern('x', generator=legacy)
    assert any(current in str(warning.message) for warning in warnings)
    assert deprecated.svg_string == GeoPattern('x', patterns=current).svg_string
