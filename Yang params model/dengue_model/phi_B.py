"""Fecundidad de *Aedes albopictus* (phi_B).

Especie: A. albopictus.
Etapa: hembra adulta.
Unidad: huevos·hembra⁻¹·ciclo⁻¹.
Ajuste: producto de dos polinomios grado 6 en T (°C):
    phi_B(T) = biting_rate(T) · fecundidad_por_mordedura(T)
Fuente: Mordecai et al. (2019) + Marini et al. — ajustes combinados.
Rango de ajuste: T ∈ [15, 35] °C.
"""
from __future__ import annotations

import numpy as np

from ._utils import clip_temp_for_poly, return_like_input
from .temp import temp


COEFF_FECUND = np.array(
    [
        0.0000116712819,
        -0.0015833228349,
        0.0854057774634,
        -2.3533940540695,
        35.0378012046865,
        -263.6780055767482,
        783.2335484007083,
    ],
    dtype=float,
)
COEFF_BR = np.array(
    [
        0.000000038135089,
        -0.000005576944503,
        0.000324339154486,
        -0.009624903256283,
        0.153953856777874,
        -1.242444992921582,
        3.931227652768022,
    ],
    dtype=float,
)


def phi_B(day):
    x_values = temp(day, 0)
    x_clipped = clip_temp_for_poly(x_values, source="phi_B")
    result = np.polyval(COEFF_BR, x_clipped) * np.polyval(COEFF_FECUND, x_clipped)
    return return_like_input(day, result)
