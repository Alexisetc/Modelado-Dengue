from __future__ import annotations

import numpy as np

from .my_parameters import P
from .temp import temp


EP = np.array([0.811, 0.939, 0.96, 0.933, 0.828, 0.485], dtype=float)
TEMP = np.array([16, 22, 25, 28, 31, 35], dtype=float)
POLYFIT = np.polyfit(TEMP, EP, 5)


def psi1_a(day):
    ep_vals = np.polyval(POLYFIT, temp(day, 0))
    return (P.mu_E_a(day) * ep_vals) / (1.0 - ep_vals)
