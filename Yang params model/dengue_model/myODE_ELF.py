from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from .my_parameters import DEFAULT_COMPETITION, P


def myODE_ELF(t, y, p=None):
    if p is None:
        p = DEFAULT_COMPETITION

    bet_ba, bet_ab = np.asarray(p, dtype=float)
    e_a, l_a, f_a, e_b, l_b, f_b = np.asarray(y, dtype=float)

    et_a = P.phi_p_a(t) * f_a - (P.mu_E_a(t) + P.psi1_a(t)) * e_a
    lt_a = P.psi1_a(t) * e_a * (1 - ((l_a + l_b - (bet_ba * l_b)) / P.K)) - (
        P.mu_L_a(t) + P.psi2_a(t)
    ) * l_a
    ft_a = P.psi2_a(t) * P.bF_a * l_a - P.mu_F_a(t) * f_a

    if t < 355:
        et_b = 0.0
        lt_b = 0.0
        ft_b = 0.0
    else:
        et_b = P.phi_p_b(t) * f_b - (P.mu_E_b(t) + P.psi1_b(t)) * e_b
        lt_b = P.psi1_b(t) * e_b * (1 - ((l_a + l_b - (bet_ab * l_a)) / P.K)) - (
            P.mu_L_b(t) + P.psi2_b(t)
        ) * l_b
        ft_b = P.psi2_b(t) * P.bF_b * l_b - P.mu_F_b(t) * f_b

    return np.array([et_a, lt_a, ft_a, et_b, lt_b, ft_b], dtype=float)


def solve_model(t_eval, y0, p=None, method="RK45"):
    t_eval = np.asarray(t_eval, dtype=float)
    y0 = np.asarray(y0, dtype=float)
    sol = solve_ivp(
        fun=lambda t, y: myODE_ELF(t, y, p),
        t_span=(float(t_eval[0]), float(t_eval[-1])),
        y0=y0,
        t_eval=t_eval,
        method=method,
    )
    if not sol.success:
        raise RuntimeError(f"solve_ivp fallo: {sol.message}")
    return sol.t, sol.y.T
