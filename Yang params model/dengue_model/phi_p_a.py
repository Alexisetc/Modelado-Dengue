"""Tasa de oviposición efectiva per cápita de *A. aegypti* (phi_p_a).

Combina la fecundidad base `phi_A(T)` con la supervivencia de la hembra
durante el ciclo de oviposición:

    phi_p = (phi_A · sigma) / (mu_F + sigma)

donde sigma es la tasa inversa del intervalo entre oviposiciones y mu_F
la mortalidad adulta. Representa huevos·hembra⁻¹·día⁻¹ útiles.

Unidad: día⁻¹ (cuando se multiplica por F en el ODE da huevos/día).
"""
from __future__ import annotations

from .muF_a import muF_a
from .my_parameters import P
from .phi_A import phi_A


def phi_p_a(day):
    return (phi_A(day) * P.sigma_a) / (muF_a(day) + P.sigma_a)
