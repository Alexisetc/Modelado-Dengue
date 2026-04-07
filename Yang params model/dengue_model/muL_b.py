from __future__ import annotations

import numpy as np

from ._utils import return_like_input
from .temp import temp


PSI_2B_COEFFS = np.array(
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
EAS_COEFFS = np.array(
    [
        0.000000027595905,
        -0.000003970863730,
        0.000231119129084,
        -0.006946993580407,
        0.109839713053612,
        -0.777893789484992,
        1.910374982086748,
    ],
    dtype=float,
)


def muL_b(day):
    x_values = temp(day, 0)
    psi_2b = np.polyval(PSI_2B_COEFFS, x_values)
    eas = np.polyval(EAS_COEFFS, x_values)
    result = psi_2b / eas - psi_2b
    return return_like_input(day, result)
