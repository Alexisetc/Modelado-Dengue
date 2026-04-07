from __future__ import annotations

import numpy as np

from ._utils import return_like_input
from .temp import temp


COEFF_FECUND = np.array(
    [
        0.0000116712819,
        -0.0015833228349,
        0.0854057774634,
        -2.3533940540695,
        35.0378012046865,
        -263.6780055767482,
        783.2335484007083,
    ],
    dtype=float,
)
COEFF_BR = np.array(
    [
        0.000000038135089,
        -0.000005576944503,
        0.000324339154486,
        -0.009624903256283,
        0.153953856777874,
        -1.242444992921582,
        3.931227652768022,
    ],
    dtype=float,
)


def phi_B(day):
    x_values = temp(day, 0)
    result = np.polyval(COEFF_BR, x_values) * np.polyval(COEFF_FECUND, x_values)
    return return_like_input(day, result)
