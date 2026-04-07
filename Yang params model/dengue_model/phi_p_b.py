from __future__ import annotations

from .muF_b import muF_b
from .my_parameters import P
from .phi_B import phi_B


def phi_p_b(day):
    return (phi_B(day) * P.sigma_b) / (muF_b(day) + P.sigma_b)
