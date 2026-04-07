from __future__ import annotations

import numpy as np

from ._utils import return_like_input
from .temp import temp


EGG_L1_COEFFS = np.array([-0.0002, 0.0139, -0.2278, 1.1650], dtype=float)
DEV_RATE_COEFFS = np.array([-0.0007, 0.0227, 0.2817, -2.3500], dtype=float)


def muE_b(day):
    x_values = temp(day, 0)
    dev_rate = np.polyval(DEV_RATE_COEFFS, x_values)
    egg_l1 = np.polyval(EGG_L1_COEFFS, x_values)
    result = dev_rate / egg_l1 - dev_rate
    return return_like_input(day, result)
