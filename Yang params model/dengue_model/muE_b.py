"""Mortalidad de huevos de *Aedes albopictus* (mu_E_b).

Etapa: huevo.
Unidad: día⁻¹.
Fórmula: mu_E = (dev_rate / egg_L1) − dev_rate
  donde dev_rate es la tasa de desarrollo huevo→L1 y egg_L1 la supervivencia
  de la etapa huevo hasta primera larva.
Fuente: Marini et al. y Mordecai et al. (2019).

El cociente explota cuando `egg_L1 → 0`; el polinomio de supervivencia se
clippea para garantizar un mínimo positivo (1e-3) y evitar divergencia.
"""
from __future__ import annotations

import numpy as np

from ._utils import clip_temp_for_poly, return_like_input
from .temp import temp


EGG_L1_COEFFS = np.array([-0.0002, 0.0139, -0.2278, 1.1650], dtype=float)
DEV_RATE_COEFFS = np.array([-0.0007, 0.0227, 0.2817, -2.3500], dtype=float)

_EGG_L1_FLOOR = 1e-3  # supervivencia mínima para evitar divergencia


def muE_b(day):
    x_vals = temp(day, 0)
    x_clipped = clip_temp_for_poly(x_vals, source="muE_b")
    dev_rate = np.polyval(DEV_RATE_COEFFS, x_clipped)
    egg_l1_raw = np.polyval(EGG_L1_COEFFS, x_clipped)
    egg_l1_safe = np.clip(egg_l1_raw, _EGG_L1_FLOOR, None)
    result = dev_rate / egg_l1_safe - dev_rate
    return return_like_input(day, result)
