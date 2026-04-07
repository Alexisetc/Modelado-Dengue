from __future__ import annotations

import numpy as np

from ._utils import return_like_input
from .temp import temp


COEFFICIENTS = np.array([-0.0, 0.0004, -0.0168, 0.3890, -4.3705, 19.0735], dtype=float)


def muE_a(day):
    x_values = temp(day, 0)
    result = 1.0 / np.polyval(COEFFICIENTS, x_values)
    return return_like_input(day, result)
