from __future__ import annotations

import numpy as np

from ._utils import return_like_input
from .temp import temp


COEFFICIENTS = np.array(
    [
        0.000000003111255,
        -0.000000510683515,
        0.000032364878841,
        -0.001035204429043,
        0.017823943160582,
        -0.150962097623919,
        0.491223455446361,
    ],
    dtype=float,
)


def psi2_b(day):
    x_values = temp(day, 0)
    result = np.polyval(COEFFICIENTS, x_values)
    return return_like_input(day, result)
