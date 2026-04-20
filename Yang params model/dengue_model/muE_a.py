"""Mortalidad de huevos de *A. aegypti* (mu_E_a).

Especie: A. aegypti.
Etapa: huevo.
Unidad: día⁻¹.
Fórmula: mu_E = 1 / polinomio_grado_5(T) — el polinomio representa el
  tiempo medio de supervivencia del huevo (días); su inversa es la tasa
  instantánea de mortalidad.
Fuente: Farnesi et al. (2009), ajuste en MATLAB original.
Rango de ajuste: T ∈ [16, 35] °C.
"""
from __future__ import annotations

import numpy as np

from ._utils import clip_temp_for_poly, return_like_input
from .temp import temp


COEFFICIENTS = np.array([-0.0, 0.0004, -0.0168, 0.3890, -4.3705, 19.0735], dtype=float)

_LIFETIME_FLOOR = 1e-3  # tiempo de vida mínimo (días) para evitar division by zero


def muE_a(day):
    x_values = temp(day, 0)
    x_clipped = clip_temp_for_poly(x_values, source="muE_a")
    lifetime = np.polyval(COEFFICIENTS, x_clipped)
    lifetime_safe = np.clip(lifetime, _LIFETIME_FLOOR, None)
    result = 1.0 / lifetime_safe
    return return_like_input(day, result)
