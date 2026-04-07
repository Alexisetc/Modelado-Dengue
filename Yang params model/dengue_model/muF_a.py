from __future__ import annotations

import numpy as np

from ._utils import return_like_input
from .temp import temp


COEFFICIENTS = np.array(
    [3.809e-06, -3.408e-04, 1.116e-02, -1.590e-01, 8.692e-01],
    dtype=float,
)


def muF_a(day):
    x_values = temp(day, 0)
    result = np.polyval(COEFFICIENTS, x_values)
    return return_like_input(day, result)
