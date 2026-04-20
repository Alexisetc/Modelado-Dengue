"""Tasa de desarrollo larva → adulto de *A. aegypti* (psi2_a).

Especie: A. aegypti.
Etapas: larva → pupa → adulto.
Unidad: día⁻¹.
Ajuste: polinomio grado 7 en T (°C).
Fuente: Yang et al. (2011).
Rango de ajuste: T ∈ [15, 35] °C.
"""
from __future__ import annotations

import numpy as np

from ._utils import clip_temp_for_poly, return_like_input
from .temp import temp


COEFFICIENTS = np.array(
    [-3.420e-10, 5.153e-08, -3.017e-06, 8.723e-05, -1.341e-03, 1.164e-02, -5.723e-02, 1.310e-01],
    dtype=float,
)


def psi2_a(day):
    x_values = temp(day, 0)
    x_clipped = clip_temp_for_poly(x_values, source="psi2_a")
    result = np.polyval(COEFFICIENTS, x_clipped)
    return return_like_input(day, result)
