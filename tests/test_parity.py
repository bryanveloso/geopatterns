import hashlib
import json
from pathlib import Path

import pytest

from geopatterns import GeoPattern

FIXTURES = Path(__file__).parent / 'fixtures'
FIXTURE_STRING = 'Mastering Markdown'

PATTERNS = [
    'chevrons',
    'concentric_circles',
    'diamonds',
    'hexagons',
    'mosaic_squares',
    'nested_squares',
    'octagons',
    'overlapping_circles',
    'overlapping_rings',
    'plaid',
    'plus_signs',
    'sine_waves',
    'squares',
    'tessellation',
    'triangles',
    'xes',
]

# Patterns whose output matches upstream. Everything else is expected to fail.
PORTED = set()


def expected_to_pass(patterns):
    # With no patterns requested, upstream picks one from the hash.
    return set(patterns or PATTERNS) <= PORTED


def mark_unported(patterns):
    if expected_to_pass(patterns):
        return []
    return [pytest.mark.xfail(strict=True, reason='not ported yet')]


def generate(string, patterns=None, color=None, base_color=None):
    options = {}
    if patterns:
        options['patterns'] = patterns
    if color:
        options['color'] = color
    if base_color:
        options['base_color'] = base_color
    return GeoPattern(string, **options)


FIXTURE_CASES = [
    (name, [name], {}) for name in PATTERNS
] + [
    ('diamonds_with_color', ['diamonds'], {'color': '#00ff00'}),
    ('diamonds_with_base_color', ['diamonds'], {'base_color': '#00ff00'}),
]


@pytest.mark.parametrize(
    'name, patterns, options',
    [pytest.param(*case, id=case[0], marks=mark_unported(case[1])) for case in FIXTURE_CASES],
)
def test_matches_upstream_fixture(name, patterns, options):
    expected = (FIXTURES / 'upstream' / f'{name}.svg').read_text().rstrip('\n')
    assert generate(FIXTURE_STRING, patterns, **options).svg_string == expected


def case_id(args):
    parts = [','.join(args.get('patterns') or ['default'])]
    parts += [f'{k}={v}' for k, v in args.items() if k in ('color', 'base_color')]
    parts.append(repr(args['string'][:24]))
    return '|'.join(parts)


HASHES = json.loads((FIXTURES / 'hashes.json').read_text())['cases']


@pytest.mark.parametrize(
    'case',
    [pytest.param(case, id=case_id(case['args']), marks=mark_unported(case['args'].get('patterns'))) for case in HASHES],
)
def test_matches_upstream_hashes(case):
    svg = generate(**case['args']).svg_string
    assert hashlib.sha256(svg.encode()).hexdigest() == case['sha256']
