"""Mortalidad de larvas de *Aedes albopictus* (mu_L_b).

Etapa: larva.
Unidad: día⁻¹.
Fórmula: mu_L = (psi2_b / EAS) − psi2_b
  donde psi2_b es la tasa de desarrollo larva→adulto y EAS la supervivencia
  egg-to-adult.
Fuente: Mordecai et al. (2019) — coeficientes ajustados a datos térmicos.

El cociente explota cuando `EAS → 0` (polinomio grado 6 puede cruzar cero
fuera del rango de ajuste); se aplica clipping mínimo para estabilidad.
"""
from __future__ import annotations

import numpy as np

from ._utils import clip_temp_for_poly, return_like_input
from .temp import temp


PSI_2B_COEFFS = np.array(
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
EAS_COEFFS = np.array(
    [
        0.000000027595905,
        -0.000003970863730,
        0.000231119129084,
        -0.006946993580407,
        0.109839713053612,
        -0.777893789484992,
        1.910374982086748,
    ],
    dtype=float,
)

_EAS_FLOOR = 1e-3  # supervivencia mínima egg-to-adult


def muL_b(day):
    x_vals = temp(day, 0)
    x_clipped = clip_temp_for_poly(x_vals, source="muL_b")
    psi_2b = np.polyval(PSI_2B_COEFFS, x_clipped)
    eas_raw = np.polyval(EAS_COEFFS, x_clipped)
    eas_safe = np.clip(eas_raw, _EAS_FLOOR, None)
    result = psi_2b / eas_safe - psi_2b
    return return_like_input(day, result)
