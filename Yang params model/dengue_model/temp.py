from __future__ import annotations

import numpy as np

from ._utils import return_like_input


def temp(day, method=0):
    day_array = np.asarray(day, dtype=float)

    if method == 1:
        so = 29.45
        c = 0.8218
        k1 = 0.7757
        k2 = 0.0
        u1 = 1.546e-08
        u2 = 0.0
        v = 0.08216
        periodic_temp = so * (
            c
            + v
            * (1 - c)
            * (0.5 * (1 + np.cos(2 * np.pi * ((day_array + 90) / 365 - u1)))) ** k1
            + (1 - v)
            * (1 - c)
            * (0.5 * (1 + np.cos(2 * np.pi * (day_array / 365 - u2)))) ** k2
        )
    else:
        so = 27.04
        c = 0.8949
        k1 = 0.7757
        u1 = 2.335e-14
        v = 0.1516
        periodic_temp = so * (
            c
            + v
            * (1 - c)
            * (0.5 * (1 + np.cos(2 * np.pi * ((day_array + 90) / 365 - u1)))) ** k1
        )

    return return_like_input(day, periodic_temp)
