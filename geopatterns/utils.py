# -*- coding: utf-8 -*-
from __future__ import unicode_literals


# Python implementation of Processing's map function
# http://processing.org/reference/map_.html
def promap(value, v_min, v_max, d_min, d_max):  # v for value, d for desired
    v_value = float(value)
    v_range = v_max - v_min
    d_range = d_max - d_min
    d_value = (v_value - v_min) * d_range / v_range + d_min
    return d_value
