"""Utilidades numéricas compartidas: preservación de dimensión, división
segura y clipping de temperatura dentro del dominio de los polinomios.
"""
from __future__ import annotations

import warnings

import numpy as np


def return_like_input(template, values):
    """Si `template` era escalar, retorna escalar; si era array, retorna array."""
    array = np.asarray(values, dtype=float)
    if np.asarray(template).ndim == 0:
        return float(array)
    return array


def safe_fraction(numerator, denominator):
    """Divide elemento a elemento; donde el denominador es 0 retorna 0 (no NaN)."""
    num = np.asarray(numerator, dtype=float)
    den = np.asarray(denominator, dtype=float)
    result = np.divide(
        num,
        den,
        out=np.zeros_like(num, dtype=float),
        where=den != 0,
    )
    return return_like_input(num, result)


def clip_temp_for_poly(x, source: str = ""):
    """Clippea `x` al dominio [poly_temp_min, poly_temp_max] de la config.

    Los polinomios biológicos fueron ajustados en un rango finito de
    temperatura. Extrapolar fuera de ese rango puede producir valores
    negativos, divergentes o numéricamente inestables. Esta función
    recorta `x` y emite un `RuntimeWarning` (controlable vía
    `config.CONFIG.warn_on_poly_extrapolation`).

    Args:
        x: temperatura (escalar o array) a evaluar en un polinomio.
        source: nombre del módulo que llama (para el warning).
    Returns:
        array float con `x` dentro del rango permitido.
    """
    from . import config  # import tardío para evitar ciclos

    cfg = config.CONFIG
    x_arr = np.asarray(x, dtype=float)

    below = x_arr < cfg.poly_temp_min
    above = x_arr > cfg.poly_temp_max
    any_below = bool(np.any(below))
    any_above = bool(np.any(above))

    if (any_below or any_above) and cfg.warn_on_poly_extrapolation:
        warnings.warn(
            f"{source or 'clip_temp_for_poly'}: temperatura fuera del dominio "
            f"[{cfg.poly_temp_min}, {cfg.poly_temp_max}] °C "
            f"(min={float(np.min(x_arr)):.3f}, max={float(np.max(x_arr)):.3f}). "
            f"Se aplica clipping para evitar extrapolación de polinomios.",
            RuntimeWarning,
            stacklevel=2,
        )

    return np.clip(x_arr, cfg.poly_temp_min, cfg.poly_temp_max)
