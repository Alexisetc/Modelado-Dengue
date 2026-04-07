from __future__ import annotations

import numpy as np

from ._utils import return_like_input
from .temp import temp


COEFFICIENTS = np.array([-1.515e-04, 1.015e-02, -2.124e-01, 1.8, -5.4], dtype=float)


def phi_A(day):
    x_values = temp(day, 0)
    result = np.polyval(COEFFICIENTS, x_values)
    return return_like_input(day, result)
