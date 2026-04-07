from __future__ import annotations

import numpy as np

from ._utils import return_like_input
from .temp import temp


COEFFICIENTS = np.array([-0.0007, 0.0227, 0.2817, -2.3500], dtype=float)


def psi1_b(day):
    x_values = temp(day, 0)
    result = np.polyval(COEFFICIENTS, x_values)
    return return_like_input(day, result)
