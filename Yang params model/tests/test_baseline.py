"""Chequeos programáticos del modelo ELF.

No dependen de MATLAB — validan propiedades estructurales y rangos
biológicos plausibles. Los tests de equivalencia numérica contra el
baseline MATLAB van en `test_matlab_parity.py` (pendiente).

Run:
    python -m pytest tests/test_baseline.py -v
"""
from __future__ import annotations

import numpy as np
import pytest

from dengue_model import CONFIG, ModelConfig, run_elf, set_config
from dengue_model.my_parameters import P, equilibrium_a, initial_state
from dengue_model.myODE_ELF import myODE_ELF
from dengue_model.temp import temp


# -----------------------------------------------------------------------------
# Fixture: simulación limpia con config por defecto
# -----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def simulation():
    set_config(ModelConfig())  # asegurar defaults
    return run_elf(plot=False)


# -----------------------------------------------------------------------------
# Propiedades estructurales
# -----------------------------------------------------------------------------

def test_no_nan_inf(simulation):
    assert np.all(np.isfinite(simulation["y"])), "y contiene NaN o inf"
    assert np.all(np.isfinite(simulation["fractions"])), "fractions contiene NaN o inf"


def test_no_negative_populations(simulation):
    y = simulation["y"]
    # Pequeña tolerancia numérica de RK45
    assert np.all(y >= -1e-6), f"y tiene valores negativos: min={y.min()}"


def test_fractions_sum_to_one(simulation):
    fr = simulation["fractions"]
    # Suma por especie (columnas 0-2 = aegypti, 3-5 = albopictus)
    sum_a = fr[:, :3].sum(axis=1)
    sum_b = fr[:, 3:].sum(axis=1)
    # Antes de la introducción de albopictus, sum_b puede ser 0 (denominador 0 → safe_fraction=0)
    assert np.allclose(sum_a, 1.0, atol=1e-10), "Fracciones aegypti no suman 1"
    # sum_b es 0 o 1 dependiendo de si albopictus está activo
    assert np.all((np.abs(sum_b - 1.0) < 1e-10) | (np.abs(sum_b) < 1e-10))


def test_output_shape(simulation):
    t = simulation["t"]
    y = simulation["y"]
    assert t.shape == (CONFIG.num_points,)
    assert y.shape == (CONFIG.num_points, 6)


# -----------------------------------------------------------------------------
# Dinámica biológica esperada
# -----------------------------------------------------------------------------

def test_albopictus_dormant_before_intro_day(simulation):
    t = simulation["t"]
    y = simulation["y"]
    intro = CONFIG.albopictus_introduction_day

    # Índices estrictamente antes del día de introducción
    mask = t < intro - 1e-6
    if not np.any(mask):
        pytest.skip("simulación no cubre el periodo pre-introducción")

    # E_b debe estar en su valor inicial (albopictus_intro_eggs), L_b y F_b en 0
    eb_pre = y[mask, 3]
    lb_pre = y[mask, 4]
    fb_pre = y[mask, 5]
    assert np.allclose(eb_pre, CONFIG.albopictus_intro_eggs, atol=1e-6), (
        f"E_b cambió antes de t={intro}: {eb_pre}"
    )
    assert np.allclose(lb_pre, 0.0, atol=1e-6), f"L_b != 0 antes de t={intro}"
    assert np.allclose(fb_pre, 0.0, atol=1e-6), f"F_b != 0 antes de t={intro}"


def test_temperature_in_biological_range():
    days = np.linspace(0, 365, 500)
    t_values = temp(days, 0)
    assert np.all(t_values >= 15), f"temp() < 15°C: min={t_values.min()}"
    assert np.all(t_values <= 40), f"temp() > 40°C: max={t_values.max()}"


def test_equilibrium_returns_positive_finite():
    eq = equilibrium_a(day=1.0)
    assert np.all(np.isfinite(eq)), "equilibrium_a devolvió no-finitos"
    assert np.all(eq > 0), f"equilibrium_a devolvió valores no positivos: {eq}"


def test_equilibrium_is_steady_state_of_ode():
    """En el equilibrio aegypti, las derivadas de E_a, L_a, F_a deben ser ~0
    (con albopictus en 0, el ODE de aegypti debe estar estacionario)."""
    y0 = initial_state()
    y0_only_aeg = y0.copy()
    y0_only_aeg[3:] = 0.0  # anular albopictus para testear solo el sub-ODE de aegypti

    derivs = myODE_ELF(t=1.0, y=y0_only_aeg, p=np.array([0.0, 0.0]))
    # Comparar contra una escala típica de las poblaciones (para permitir tol relativa)
    scale = max(float(np.max(y0_only_aeg[:3])), 1.0)
    aeg_derivs = derivs[:3]
    assert np.all(np.abs(aeg_derivs) / scale < 1e-3), (
        f"equilibrium_a no es punto fijo. Derivadas aegypti relativas: "
        f"{(aeg_derivs / scale).tolist()}"
    )


# -----------------------------------------------------------------------------
# Rangos biológicos plausibles de las tasas (Yang 2011, Mordecai 2019)
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("T_test,expected_range", [
    # A 25°C (óptimo), la mortalidad adulta base de aegypti debe ser ~0.02-0.15/día
    (25, (0.01, 0.2)),
])
def test_muF_a_base_range(T_test, expected_range):
    """muF_a (sin el multiplicador empírico) debe caer en rango biológico."""
    # Evaluar directamente en el día cuya temp es aprox T_test
    # temp(d=0) con defaults ≈ 27.04°C, así que usamos día 90 (temp ≈ baseline·c)
    from dengue_model.muF_a import muF_a
    rates = [muF_a(d) for d in [0, 90, 180, 270]]
    lo, hi = expected_range
    assert all(lo <= r <= hi for r in rates), (
        f"muF_a fuera de [{lo}, {hi}]: {rates}"
    )


def test_phi_A_produces_positive_fecundity():
    from dengue_model.phi_A import phi_A
    rates = [phi_A(d) for d in [0, 90, 180, 270, 360]]
    assert all(r > 0 for r in rates), f"phi_A no positiva: {rates}"


def test_psi2_a_positive_and_bounded():
    from dengue_model.psi2_a import psi2_a
    rates = np.array([psi2_a(d) for d in np.linspace(0, 365, 50)])
    assert np.all(rates > 0), "psi2_a tiene valores no positivos"
    assert np.all(rates < 1.0), f"psi2_a > 1/día (implausible): max={rates.max()}"


# -----------------------------------------------------------------------------
# Sensibilidad a config
# -----------------------------------------------------------------------------

def test_config_override_propagates(tmp_path):
    """Cambiar beta_ba vía set_config debe reflejarse en default_competition."""
    from dengue_model.my_parameters import default_competition

    cfg = ModelConfig(beta_ba=0.1, beta_ab=0.9)
    set_config(cfg)
    assert default_competition().tolist() == [0.1, 0.9]
    assert P.albopictus_introduction_day == 355.0  # default inalterado

    # Restaurar
    set_config(ModelConfig())


def test_config_intro_day_parametrized():
    """Cambiar albopictus_introduction_day debe afectar el ODE."""
    cfg = ModelConfig(albopictus_introduction_day=100.0)
    set_config(cfg)
    try:
        result = run_elf(plot=False)
        # Albopictus debe estar activo desde t=100, no desde t=355
        t = result["t"]
        y = result["y"]
        # Buscar primer índice donde t > 110
        idx = np.searchsorted(t, 110.0)
        if idx < len(t):
            # E_b debe haber cambiado (ya sea creciendo o decreciendo)
            assert y[idx, 3] != CONFIG.albopictus_intro_eggs or y[idx, 4] > 0 or y[idx, 5] > 0, (
                "albopictus no se activó con intro_day=100"
            )
    finally:
        set_config(ModelConfig())
