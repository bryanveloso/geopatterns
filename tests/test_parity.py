import hashlib
import json
from pathlib import Path

import pytest

from geopatterns import GeoPattern
from geopatterns.patterns import PATTERNS as registered

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

def test_patterns_are_in_upstream_order():
    # With no pattern requested, the hash picks one by index.
    assert list(registered) == PATTERNS


FIXTURE_CASES = [
    (name, [name], {}) for name in PATTERNS
] + [
    ('diamonds_with_color', ['diamonds'], {'color': '#00ff00'}),
    ('diamonds_with_base_color', ['diamonds'], {'base_color': '#00ff00'}),
]


@pytest.mark.parametrize('name, patterns, options', FIXTURE_CASES, ids=[case[0] for case in FIXTURE_CASES])
def test_matches_upstream_fixture(name, patterns, options):
    expected = (FIXTURES / 'upstream' / f'{name}.svg').read_text().rstrip('\n')
    assert GeoPattern(FIXTURE_STRING, patterns=patterns, **options).svg_string == expected


def case_id(args):
    parts = [','.join(args.get('patterns') or ['default'])]
    parts += [f'{k}={v}' for k, v in args.items() if k in ('color', 'base_color')]
    parts.append(repr(args['string'][:24]))
    return '|'.join(parts)


HASHES = json.loads((FIXTURES / 'hashes.json').read_text())['cases']


@pytest.mark.parametrize('case', HASHES, ids=[case_id(case['args']) for case in HASHES])
def test_matches_upstream_hashes(case):
    svg = GeoPattern(**case['args']).svg_string
    assert hashlib.sha256(svg.encode()).hexdigest() == case['sha256']
