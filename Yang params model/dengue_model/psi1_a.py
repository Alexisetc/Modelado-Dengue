"""Tasa de desarrollo huevo → larva de *Aedes aegypti* (psi1_a).

Etapa origen: huevo.
Etapa destino: larva (L1).
Unidad: día⁻¹.
Fórmula: psi1 = (mu_E · EP) / (1 − EP)  con EP = fracción de huevos eclosados.
Fuente: Farnesi et al. (2009) — datos experimentales a 6 temperaturas.
Rango de ajuste: T ∈ [16, 35] °C (fuera se clippea y se emite warning).

La relación (mu_E · EP)/(1 − EP) puede explotar si EP → 1; `EP` se recorta
a [0, 0.999] para garantizar un denominador > 1e-3.
"""
from __future__ import annotations

import numpy as np

from ._utils import clip_temp_for_poly, return_like_input
from .my_parameters import P
from .temp import temp


EP = np.array([0.811, 0.939, 0.96, 0.933, 0.828, 0.485], dtype=float)
TEMP = np.array([16, 22, 25, 28, 31, 35], dtype=float)
POLYFIT = np.polyfit(TEMP, EP, 5)


def psi1_a(day):
    x_vals = temp(day, 0)
    x_clipped = clip_temp_for_poly(x_vals, source="psi1_a")
    ep_raw = np.polyval(POLYFIT, x_clipped)
    # EP es una fracción en [0, 1]; clippeamos para garantizar denominador > 0
    ep_safe = np.clip(ep_raw, 0.0, 0.999)
    result = (P.mu_E_a(day) * ep_safe) / (1.0 - ep_safe)
    return return_like_input(day, result)
