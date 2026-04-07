from __future__ import annotations

import numpy as np

from ._utils import return_like_input
from .temp import temp


# MATLAB usa polyval(fliplr(coefficients), x), asi que aqui los almacenamos
# ya invertidos para reproducir exactamente ese comportamiento.
COEFFICIENTS = np.array([6.794e-06, -6.778e-04, 2.457e-02, -3.797e-01, 2.130], dtype=float)


def muL_a(day):
    x_values = temp(day, 0)
    result = np.polyval(COEFFICIENTS, x_values)
    return return_like_input(day, result)
