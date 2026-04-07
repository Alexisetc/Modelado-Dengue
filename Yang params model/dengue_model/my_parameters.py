from __future__ import annotations

from types import SimpleNamespace

import numpy as np


P = SimpleNamespace()
P.K = 10**5
P.bF_a = 0.5
P.bM_a = 0.5
P.sigma_a = 1.0
P.bF_b = 0.5
P.bM_b = 0.5
P.sigma_b = 1.0


from .muE_a import muE_a
from .muE_b import muE_b
from .muF_a import muF_a
from .muF_b import muF_b
from .muL_a import muL_a
from .muL_b import muL_b
from .phi_A import phi_A
from .phi_B import phi_B
from .phi_p_a import phi_p_a
from .phi_p_b import phi_p_b
from .psi1_a import psi1_a
from .psi1_b import psi1_b
from .psi2_a import psi2_a
from .psi2_b import psi2_b


P.phi_a = phi_A
P.psi1_a = psi1_a
P.psi2_a = psi2_a
P.mu_E_a = muE_a
P.mu_L_a = muL_a
P.mu_F_a = lambda t: muF_a(t) * 3.0
P.phi_p_a = phi_p_a

P.phi_b = phi_B
P.psi1_b = psi1_b
P.psi2_b = psi2_b
P.mu_E_b = muE_b
P.mu_L_b = muL_b
P.mu_F_b = lambda t: muF_b(t) * 10.0
P.phi_p_b = phi_p_b

DEFAULT_COMPETITION = np.array([0.5, 0.5], dtype=float)


def equilibrium_a(day=1.0):
    ga0 = (
        P.bF_a
        * (P.psi1_a(day) / (P.mu_E_a(day) + P.psi1_a(day)))
        * (P.psi2_a(day) / (P.mu_L_a(day) + P.psi2_a(day)))
        * (P.phi_p_a(day) / P.mu_F_a(day))
    )
    la0 = P.K * (1.0 - (1.0 / ga0))
    fa0 = P.bF_a * (P.psi2_a(day) / P.mu_F_a(day)) * la0
    ea0 = (
        P.bF_a
        * (P.phi_p_a(day) / (P.mu_E_a(day) + P.psi1_a(day)))
        * (P.psi2_a(day) / P.mu_F_a(day))
        * la0
    )
    return np.array([ea0, la0, fa0], dtype=float)


def initial_state(day=1.0):
    ea0, la0, fa0 = equilibrium_a(day)
    return np.array([ea0, la0, fa0, 10.0, 0.0, 0.0], dtype=float)
