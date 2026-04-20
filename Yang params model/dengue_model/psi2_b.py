"""Tasa de desarrollo larva → adulto de *A. albopictus* (psi2_b).

Especie: A. albopictus.
Etapas: larva → pupa → adulto.
Unidad: día⁻¹.
Ajuste: polinomio grado 6 en T (°C).
Fuente: Mordecai et al. (2019).
Rango de ajuste: T ∈ [15, 35] °C.
"""
from __future__ import annotations

import numpy as np

from ._utils import clip_temp_for_poly, return_like_input
from .temp import temp


COEFFICIENTS = np.array(
    [
        0.000000003111255,
        -0.000000510683515,
        0.000032364878841,
        -0.001035204429043,
        0.017823943160582,
        -0.150962097623919,
        0.491223455446361,
    ],
    dtype=float,
)


def psi2_b(day):
    x_values = temp(day, 0)
    x_clipped = clip_temp_for_poly(x_values, source="psi2_b")
    result = np.polyval(COEFFICIENTS, x_clipped)
    return return_like_input(day, result)
