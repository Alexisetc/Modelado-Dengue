"""Mortalidad de hembras adultas de *A. albopictus* (mu_F_b base).

Especie: A. albopictus.
Etapa: hembra adulta.
Unidad: día⁻¹.
Fórmula: mu_F = 1 / (1000·polinomio_grado_5(T)) — el polinomio (escalado por
  1000) representa el tiempo medio de vida del adulto en días; su inversa es
  la tasa de mortalidad instantánea.
Fuente: Mordecai et al. (2019).
Rango de ajuste: T ∈ [15, 35] °C.

Nota: en el modelo ELF la mortalidad efectiva es
`muF_b(t) · config.mortality_adjustment_albopictus`. El multiplicador (10.0
por defecto) viene del MATLAB original.
"""
from __future__ import annotations

import numpy as np

from ._utils import clip_temp_for_poly, return_like_input
from .temp import temp


COEFFICIENTS = 1000.0 * np.array(
    [
        -0.000000280151205,
        0.000038830897223,
        -0.002030126893948,
        0.049162298893216,
        -0.540751134100950,
        2.180587170776479,
    ],
    dtype=float,
)

_LIFETIME_FLOOR = 1e-3  # piso del polinomio para evitar división por cero


def muF_b(day):
    x_values = temp(day, 0)
    x_clipped = clip_temp_for_poly(x_values, source="muF_b")
    lifetime = np.polyval(COEFFICIENTS, x_clipped)
    lifetime_safe = np.clip(lifetime, _LIFETIME_FLOOR, None)
    result = 1.0 / lifetime_safe
    return return_like_input(day, result)
