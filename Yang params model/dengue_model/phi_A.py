"""Fecundidad de *Aedes aegypti* (phi_A).

Especie: A. aegypti.
Etapa: hembra adulta.
Unidad: huevos·hembra⁻¹·ciclo⁻¹.
Ajuste: polinomio grado 4 en T (°C).
Fuente: Yang et al. (2011) — Table 2.
Rango de ajuste: T ∈ [15, 35] °C.
"""
from __future__ import annotations

import numpy as np

from ._utils import clip_temp_for_poly, return_like_input
from .temp import temp


COEFFICIENTS = np.array([-1.515e-04, 1.015e-02, -2.124e-01, 1.8, -5.4], dtype=float)


def phi_A(day):
    x_values = temp(day, 0)
    x_clipped = clip_temp_for_poly(x_values, source="phi_A")
    result = np.polyval(COEFFICIENTS, x_clipped)
    return return_like_input(day, result)
