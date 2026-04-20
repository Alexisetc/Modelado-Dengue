"""Sistema de ODEs del modelo ELF (6 compartimentos, 2 especies).

Estado `y` (shape (6,)):
    y[0] = E_a  (huevos de A. aegypti)
    y[1] = L_a  (larvas de A. aegypti)
    y[2] = F_a  (hembras adultas de A. aegypti)
    y[3] = E_b  (huevos de A. albopictus)
    y[4] = L_b  (larvas de A. albopictus)
    y[5] = F_b  (hembras adultas de A. albopictus)

Parámetro `p = [beta_ba, beta_ab]`: coeficientes de competencia interespecífica
sobre el término logístico larval. A. albopictus permanece inactivo hasta el
día `P.albopictus_introduction_day` (configurable).
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from . import config
from .my_parameters import P, default_competition


def myODE_ELF(t, y, p=None):
    if p is None:
        p = default_competition()

    bet_ba, bet_ab = np.asarray(p, dtype=float)
    e_a, l_a, f_a, e_b, l_b, f_b = np.asarray(y, dtype=float)

    et_a = P.phi_p_a(t) * f_a - (P.mu_E_a(t) + P.psi1_a(t)) * e_a
    lt_a = P.psi1_a(t) * e_a * (1 - ((l_a + l_b - (bet_ba * l_b)) / P.K)) - (
        P.mu_L_a(t) + P.psi2_a(t)
    ) * l_a
    ft_a = P.psi2_a(t) * P.bF_a * l_a - P.mu_F_a(t) * f_a

    if t < P.albopictus_introduction_day:
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


def solve_model(t_eval, y0, p=None, method=None, rtol=None, atol=None):
    """Integra el ODE con diagnósticos de estado.

    Usa los valores de `config.CONFIG` para method/rtol/atol si no se pasan.
    Lanza `RuntimeError` con contexto detallado si `solve_ivp` falla.
    """
    cfg = config.CONFIG
    method = method or cfg.ode_method
    rtol = cfg.ode_rtol if rtol is None else rtol
    atol = cfg.ode_atol if atol is None else atol

    t_eval = np.asarray(t_eval, dtype=float)
    y0 = np.asarray(y0, dtype=float)

    if not np.all(np.isfinite(y0)):
        raise ValueError(
            f"solve_model: y0 contiene valores no finitos: {y0.tolist()}"
        )
    if np.any(y0 < 0):
        raise ValueError(
            f"solve_model: y0 contiene valores negativos: {y0.tolist()}"
        )

    sol = solve_ivp(
        fun=lambda t, y: myODE_ELF(t, y, p),
        t_span=(float(t_eval[0]), float(t_eval[-1])),
        y0=y0,
        t_eval=t_eval,
        method=method,
        rtol=rtol,
        atol=atol,
    )
    if not sol.success:
        last_t = float(sol.t[-1]) if len(sol.t) else float(t_eval[0])
        raise RuntimeError(
            f"solve_ivp falló (status={sol.status}) en t={last_t:.3f}: "
            f"{sol.message}. y0={y0.tolist()}"
        )

    y = sol.y.T
    if not np.all(np.isfinite(y)):
        bad_idx = np.argwhere(~np.isfinite(y))
        raise RuntimeError(
            f"solve_ivp produjo valores no finitos en {len(bad_idx)} celdas "
            f"(primer ocurrencia: t={sol.t[bad_idx[0, 0]]:.3f}, "
            f"compartimento={bad_idx[0, 1]})."
        )
    return sol.t, y
