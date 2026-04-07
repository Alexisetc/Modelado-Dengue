from __future__ import annotations

from .muF_a import muF_a
from .my_parameters import P
from .phi_A import phi_A


def phi_p_a(day):
    return (phi_A(day) * P.sigma_a) / (muF_a(day) + P.sigma_a)
