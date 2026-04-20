"""Modelo periódico de temperatura anual (ciclo de 365 días).

`temp(day, method=0)` retorna °C para un día (escalar o vector).

El método 0 (default) replica el modelo simplificado del MATLAB original,
con parámetros leídos de `config.CONFIG`:
    T(d) = so · [c + v·(1−c) · (½·(1+cos(2π·((d+phase)/365 − u1))))^k1]

donde `so=temp_baseline_c`, `c=temp_offset`, `v=temp_amplitude`,
`k1=temp_shape_k1`, `phase=temp_phase_days`, `u1=temp_phase_offset`.

El método 1 mantiene la forma extendida original (dos términos periódicos)
con constantes fijas — útil solo para validar contra MATLAB si alguna vez
se activó esa rama. No se expone en la configuración.
"""
from __future__ import annotations

import numpy as np

from . import config
from ._utils import return_like_input


def temp(day, method: int = 0):
    day_array = np.asarray(day, dtype=float)

    if method == 1:
        # Forma extendida del MATLAB original. No parametrizada (uso legacy).
        so = 29.45
        c = 0.8218
        k1 = 0.7757
        k2 = 0.0
        u1 = 1.546e-08
        u2 = 0.0
        v = 0.08216
        periodic_temp = so * (
            c
            + v
            * (1 - c)
            * (0.5 * (1 + np.cos(2 * np.pi * ((day_array + 90) / 365 - u1)))) ** k1
            + (1 - v)
            * (1 - c)
            * (0.5 * (1 + np.cos(2 * np.pi * (day_array / 365 - u2)))) ** k2
        )
    else:
        cfg = config.CONFIG
        periodic_temp = cfg.temp_baseline_c * (
            cfg.temp_offset
            + cfg.temp_amplitude
            * (1 - cfg.temp_offset)
            * (
                0.5
                * (
                    1
                    + np.cos(
                        2
                        * np.pi
                        * ((day_array + cfg.temp_phase_days) / 365 - cfg.temp_phase_offset)
                    )
                )
            )
            ** cfg.temp_shape_k1
        )

    return return_like_input(day, periodic_temp)
