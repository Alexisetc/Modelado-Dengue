from __future__ import annotations

import numpy as np


def return_like_input(template, values):
    array = np.asarray(values, dtype=float)
    if np.asarray(template).ndim == 0:
        return float(array)
    return array


def safe_fraction(numerator, denominator):
    num = np.asarray(numerator, dtype=float)
    den = np.asarray(denominator, dtype=float)
    result = np.divide(
        num,
        den,
        out=np.zeros_like(num, dtype=float),
        where=den != 0,
    )
    return return_like_input(num, result)
