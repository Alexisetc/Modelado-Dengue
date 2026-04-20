"""Tasa de desarrollo huevo → larva de *A. albopictus* (psi1_b).

Especie: A. albopictus.
Etapas: huevo → L1 (primera larva).
Unidad: día⁻¹.
Ajuste: polinomio grado 3 en T (°C).
Fuente: Marini et al.
Rango de ajuste: T ∈ [15, 35] °C.
"""
from __future__ import annotations

import numpy as np

from ._utils import clip_temp_for_poly, return_like_input
from .temp import temp


COEFFICIENTS = np.array([-0.0007, 0.0227, 0.2817, -2.3500], dtype=float)


def psi1_b(day):
    x_values = temp(day, 0)
    x_clipped = clip_temp_for_poly(x_values, source="psi1_b")
    result = np.polyval(COEFFICIENTS, x_clipped)
    return return_like_input(day, result)
