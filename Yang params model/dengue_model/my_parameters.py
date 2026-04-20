"""Objeto singleton `P` con parámetros globales + condiciones iniciales.

`P` es la fachada que usan el ODE y todas las funciones biológicas para
acceder a los parámetros escalares (`P.K`, `P.bF_a`, `P.sigma_a`, etc.)
y a las referencias de funciones (`P.phi_a`, `P.mu_F_a`, ...).

Los valores escalares se leen de `config.CONFIG` vía `rebuild_P()`. Las
funciones que aplican multiplicadores empíricos (`mu_F_a`, `mu_F_b`) son
lambdas que consultan `config.CONFIG` en cada llamada, de modo que los
cambios de config se reflejan sin rebuild explícito.
"""
from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from . import config


# P debe existir ANTES de los imports de funciones biológicas,
# porque varios módulos (phi_p_a, phi_p_b, psi1_a) hacen
# `from .my_parameters import P` al cargarse.
P = SimpleNamespace()


from .muE_a import muE_a  # noqa: E402
from .muE_b import muE_b  # noqa: E402
from .muF_a import muF_a  # noqa: E402
from .muF_b import muF_b  # noqa: E402
from .muL_a import muL_a  # noqa: E402
from .muL_b import muL_b  # noqa: E402
from .phi_A import phi_A  # noqa: E402
from .phi_B import phi_B  # noqa: E402
from .phi_p_a import phi_p_a  # noqa: E402
from .phi_p_b import phi_p_b  # noqa: E402
from .psi1_a import psi1_a  # noqa: E402
from .psi1_b import psi1_b  # noqa: E402
from .psi2_a import psi2_a  # noqa: E402
from .psi2_b import psi2_b  # noqa: E402


def rebuild_P() -> None:
    """Repuebla `P` con los valores actuales de `config.CONFIG`.

    Llamar tras modificar `config.CONFIG` para que los atributos escalares
    reflejen los nuevos valores. Las lambdas que leen CONFIG en runtime
    (mu_F_a, mu_F_b) no requieren rebuild.
    """
    cfg = config.CONFIG

    # Escalares
    P.K = cfg.carrying_capacity
    P.bF_a = cfg.bF_aegypti
    P.bM_a = cfg.bM_aegypti
    P.sigma_a = cfg.sigma_aegypti
    P.bF_b = cfg.bF_albopictus
    P.bM_b = cfg.bM_albopictus
    P.sigma_b = cfg.sigma_albopictus
    P.albopictus_introduction_day = cfg.albopictus_introduction_day
    P.albopictus_intro_eggs = cfg.albopictus_intro_eggs

    # Referencias de función — aegypti
    P.phi_a = phi_A
    P.psi1_a = psi1_a
    P.psi2_a = psi2_a
    P.mu_E_a = muE_a
    P.mu_L_a = muL_a
    P.mu_F_a = lambda t: muF_a(t) * config.CONFIG.mortality_adjustment_aegypti
    P.phi_p_a = phi_p_a

    # Referencias de función — albopictus
    P.phi_b = phi_B
    P.psi1_b = psi1_b
    P.psi2_b = psi2_b
    P.mu_E_b = muE_b
    P.mu_L_b = muL_b
    P.mu_F_b = lambda t: muF_b(t) * config.CONFIG.mortality_adjustment_albopictus
    P.phi_p_b = phi_p_b


rebuild_P()


def default_competition() -> np.ndarray:
    """Retorna betas actuales [beta_ba, beta_ab] leyendo CONFIG en runtime."""
    return np.array([config.CONFIG.beta_ba, config.CONFIG.beta_ab], dtype=float)


# Snapshot al import para compatibilidad con código que espera una constante.
DEFAULT_COMPETITION = default_competition()


def equilibrium_a(day: float = 1.0) -> np.ndarray:
    """Calcula el equilibrio demográfico de A. aegypti en el día `day`.

    Evalúa las tasas dependientes de temperatura en `day` y resuelve el
    punto fijo (dE/dt, dL/dt, dF/dt) = 0 para la especie A.

    Retorna:
        np.array([ea0, la0, fa0]) — huevos, larvas, hembras adultas.

    Lanza:
        ValueError — si `ga0 <= 1` (población no sostenible) o si algún
        valor resulta no finito/negativo.
    """
    psi1 = P.psi1_a(day)
    mu_e = P.mu_E_a(day)
    psi2 = P.psi2_a(day)
    mu_l = P.mu_L_a(day)
    phi_p = P.phi_p_a(day)
    mu_f = P.mu_F_a(day)

    ga0 = (
        P.bF_a
        * (psi1 / (mu_e + psi1))
        * (psi2 / (mu_l + psi2))
        * (phi_p / mu_f)
    )

    if not np.isfinite(ga0):
        raise ValueError(
            f"equilibrium_a: ga0 no finito en day={day} (ga0={ga0}). "
            f"Revisa que las tasas biológicas sean finitas en esa temperatura."
        )

    if ga0 <= 1.0:
        msg = (
            f"equilibrium_a: ga0={ga0:.4f} <= 1 en day={day}. "
            f"La población A. aegypti no es sostenible con los parámetros actuales "
            f"(mortality_adjustment_aegypti={config.CONFIG.mortality_adjustment_aegypti}). "
            f"Cada hembra produce menos de una hembra adulta en promedio."
        )
        if config.CONFIG.strict_equilibrium:
            raise ValueError(msg)
        # Modo permisivo: población cero
        import warnings
        warnings.warn(msg, RuntimeWarning, stacklevel=2)
        return np.array([0.0, 0.0, 0.0], dtype=float)

    la0 = P.K * (1.0 - (1.0 / ga0))
    fa0 = P.bF_a * (psi2 / mu_f) * la0
    ea0 = (
        P.bF_a
        * (phi_p / (mu_e + psi1))
        * (psi2 / mu_f)
        * la0
    )

    result = np.array([ea0, la0, fa0], dtype=float)
    if not np.all(np.isfinite(result)):
        raise ValueError(
            f"equilibrium_a: valores no finitos en day={day}: {result.tolist()}"
        )
    if np.any(result < 0):
        raise ValueError(
            f"equilibrium_a: valores negativos en day={day}: {result.tolist()}"
        )
    return result


def initial_state(day: float = 1.0) -> np.ndarray:
    """Estado inicial del ODE: equilibrio aegypti + inyección albopictus.

    Índices del vector retornado:
        0 = E_a (huevos aegypti)
        1 = L_a (larvas aegypti)
        2 = F_a (hembras aegypti)
        3 = E_b (huevos albopictus)  — inyectado con `albopictus_intro_eggs`
        4 = L_b (larvas albopictus)  — 0
        5 = F_b (hembras albopictus) — 0
    """
    ea0, la0, fa0 = equilibrium_a(day)
    return np.array(
        [ea0, la0, fa0, config.CONFIG.albopictus_intro_eggs, 0.0, 0.0],
        dtype=float,
    )
