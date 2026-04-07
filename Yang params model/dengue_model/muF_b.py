from __future__ import annotations

import numpy as np

from ._utils import return_like_input
from .temp import temp


COEFFICIENTS = 1000.0 * np.array(
    [
        -0.000000280151205,
        0.000038830897223,
        -0.002030126893948,
        0.049162298893216,
        -0.540751134100950,
        2.180587170776479,
    ],
    dtype=float,
)


def muF_b(day):
    x_values = temp(day, 0)
    result = 1.0 / np.polyval(COEFFICIENTS, x_values)
    return return_like_input(day, result)
