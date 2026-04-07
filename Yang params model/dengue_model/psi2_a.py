from __future__ import annotations

import numpy as np

from ._utils import return_like_input
from .temp import temp


COEFFICIENTS = np.array(
    [-3.420e-10, 5.153e-08, -3.017e-06, 8.723e-05, -1.341e-03, 1.164e-02, -5.723e-02, 1.310e-01],
    dtype=float,
)


def psi2_a(day):
    x_values = temp(day, 0)
    result = np.polyval(COEFFICIENTS, x_values)
    return return_like_input(day, result)
