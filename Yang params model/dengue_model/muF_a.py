"""Mortalidad de hembras adultas de *A. aegypti* (mu_F_a base).

Especie: A. aegypti.
Etapa: hembra adulta.
Unidad: día⁻¹.
Ajuste: polinomio grado 4 en T (°C).
Fuente: Yang et al. (2011).
Rango de ajuste: T ∈ [15, 35] °C.

Nota: en el modelo ELF la mortalidad efectiva es
`muF_a(t) · config.mortality_adjustment_aegypti` (ver my_parameters.P.mu_F_a).
El multiplicador (3.0 por defecto) proviene del MATLAB original y se
mantiene por compatibilidad — debe revisarse con los autores del modelo.
"""
from __future__ import annotations

import numpy as np

from ._utils import clip_temp_for_poly, return_like_input
from .temp import temp


COEFFICIENTS = np.array(
    [3.809e-06, -3.408e-04, 1.116e-02, -1.590e-01, 8.692e-01],
    dtype=float,
)


def muF_a(day):
    x_values = temp(day, 0)
    x_clipped = clip_temp_for_poly(x_values, source="muF_a")
    result = np.polyval(COEFFICIENTS, x_clipped)
    return return_like_input(day, result)
