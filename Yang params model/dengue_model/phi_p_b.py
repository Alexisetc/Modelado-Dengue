"""Tasa de oviposición efectiva per cápita de *A. albopictus* (phi_p_b).

Análogo a phi_p_a pero para A. albopictus:
    phi_p = (phi_B · sigma_b) / (mu_F_b + sigma_b)

Unidad: día⁻¹.
"""
from __future__ import annotations

from .muF_b import muF_b
from .my_parameters import P
from .phi_B import phi_B


def phi_p_b(day):
    return (phi_B(day) * P.sigma_b) / (muF_b(day) + P.sigma_b)
