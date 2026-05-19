"""
Genera las figuras del documento `Parametros_Aedes_albopictus.md`/`.tex`.

Produce dos archivos PNG en `figures/`:

* `albopictus_egg_stage.png` -- estadio de huevo segun Delatte et al. (2009):
  probabilidad de eclosion p_b(T), tiempo de embriogenesis tau_b(T), tasa de
  eclosion efectiva psi_{1b}(T) y mortalidad de huevo mu_{Eb}(T).

* `albopictus_params_overview.png` -- panel 2x3 con funciones continuas de
  respuesta termica para Ae. albopictus (linea continua) y Ae. aegypti (linea
  discontinua) en el rango 5-45 C. Parametros de Mordecai et al. (2017, Tabla
  S1).

Uso:

    python plot_albopictus_params.py

Requisitos: numpy, matplotlib, pandas.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
FIG_DIR = HERE / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Funciones de respuesta termica
# ---------------------------------------------------------------------------

def briere(T: np.ndarray, q: float, Tmin: float, Tmax: float) -> np.ndarray:
    """Briere asimetrica: f(T) = q*T*(T-Tmin)*sqrt(Tmax-T) en [Tmin, Tmax]."""
    T = np.asarray(T, dtype=float)
    out = np.zeros_like(T)
    mask = (T >= Tmin) & (T <= Tmax)
    Tm = T[mask]
    out[mask] = q * Tm * (Tm - Tmin) * np.sqrt(np.maximum(Tmax - Tm, 0.0))
    return out


def quadratic(T: np.ndarray, q: float, Tmin: float, Tmax: float) -> np.ndarray:
    """Cuadratica simetrica: f(T) = -q*(T-Tmin)*(T-Tmax) en [Tmin, Tmax]."""
    T = np.asarray(T, dtype=float)
    out = np.zeros_like(T)
    mask = (T >= Tmin) & (T <= Tmax)
    Tm = T[mask]
    out[mask] = -q * (Tm - Tmin) * (Tm - Tmax)
    return out


# ---------------------------------------------------------------------------
# Parametros (Mordecai et al. 2017, Tabla S1)
# ---------------------------------------------------------------------------

PARAMS_ALBOPICTUS = {
    "a":    {"fn": briere,    "q": 1.90e-4, "Tmin": 10.4, "Tmax": 38.1, "Topt": 31.8,
             "unit": r"dia$^{-1}$"},
    "EFOC": {"fn": briere,    "q": 4.77e-2, "Tmin":  7.9, "Tmax": 35.6, "Topt": 29.4,
             "unit": "huevos/ciclo"},
    "MDR":  {"fn": briere,    "q": 6.33e-5, "Tmin":  8.7, "Tmax": 39.6, "Topt": 32.6,
             "unit": r"dia$^{-1}$"},
    "pEA":  {"fn": quadratic, "q": 3.56e-3, "Tmin":  9.1, "Tmax": 39.3, "Topt": 24.2,
             "unit": "adim."},
    "lf":   {"fn": quadratic, "q": 1.39,    "Tmin": 13.5, "Tmax": 31.4, "Topt": 22.5,
             "unit": "dias"},
}

PARAMS_AEGYPTI = {
    "a":    {"fn": briere,    "q": 2.02e-4, "Tmin": 13.8, "Tmax": 40.0,
             "unit": r"dia$^{-1}$"},
    "EFD":  {"fn": briere,    "q": 8.16e-3, "Tmin": 14.7, "Tmax": 34.4,
             "unit": "huevos/dia"},
    "MDR":  {"fn": briere,    "q": 7.83e-5, "Tmin": 11.6, "Tmax": 39.1,
             "unit": r"dia$^{-1}$"},
    "pEA":  {"fn": quadratic, "q": 5.99e-3, "Tmin": 13.6, "Tmax": 38.3,
             "unit": "adim."},
    "lf":   {"fn": quadratic, "q": 0.144,   "Tmin":  9.0, "Tmax": 37.7,
             "unit": "dias"},
}


def evaluate(params: dict, key: str, T: np.ndarray) -> np.ndarray:
    p = params[key]
    return p["fn"](T, p["q"], p["Tmin"], p["Tmax"])


# ---------------------------------------------------------------------------
# Figura 1: estadio de huevo (Delatte et al. 2009)
# ---------------------------------------------------------------------------

DELATTE = pd.DataFrame(
    {
        "T":     [5,   10,  15,  20,  25,  30,  35,  40],
        "n":     [180, 100, 110, 130, 130, 140, 190, 100],
        "p_pct": [4.4, 4.0, 8.2, 66.9, 49.2, 51.4, 10.0, 0.0],
        "tau":   [11.0, 2.0, 7.4, 2.9, 4.5, 6.7, 7.1, np.nan],
        "tau_sd":[1.3,  0.0, 1.8, 0.4, 0.7, 0.7, 0.8, np.nan],
    }
)


def plot_egg_stage(out: Path) -> None:
    df = DELATTE.copy()
    df["p"] = df["p_pct"] / 100.0
    df["psi1"] = df["p"] / df["tau"]
    df["mu_E"] = (1 - df["p"]) / df["tau"]

    fig, axes = plt.subplots(2, 2, figsize=(10, 7.5), constrained_layout=True)

    ax = axes[0, 0]
    ax.plot(df["T"], df["p"], "o-", color="#1f6feb", lw=1.5)
    ax.set_xlabel("Temperatura (°C)")
    ax.set_ylabel(r"$p_b(T)$ (probabilidad de eclosion)")
    ax.set_title(r"Probabilidad de eclosion $p_b$")
    ax.grid(alpha=0.3)
    ax.set_ylim(-0.02, 1.0)

    ax = axes[0, 1]
    ax.errorbar(df["T"], df["tau"], yerr=df["tau_sd"], fmt="o-",
                color="#a3306e", lw=1.5, capsize=3)
    ax.set_xlabel("Temperatura (°C)")
    ax.set_ylabel(r"$\tau_b(T)$ (dias)")
    ax.set_title(r"Tiempo de embriogenesis $\tau_b$")
    ax.grid(alpha=0.3)

    ax = axes[1, 0]
    ax.plot(df["T"], df["psi1"], "o-", color="#1f8a3c", lw=1.5)
    ax.set_xlabel("Temperatura (°C)")
    ax.set_ylabel(r"$\psi_{1b}(T) = p_b/\tau_b$ (dia$^{-1}$)")
    ax.set_title(r"Tasa de eclosion efectiva $\psi_{1b}$")
    ax.grid(alpha=0.3)

    ax = axes[1, 1]
    ax.plot(df["T"], df["mu_E"], "o-", color="#c0392b", lw=1.5)
    ax.set_xlabel("Temperatura (°C)")
    ax.set_ylabel(r"$\mu_{Eb}(T) = (1-p_b)/\tau_b$ (dia$^{-1}$)")
    ax.set_title(r"Mortalidad de huevo $\mu_{Eb}$")
    ax.grid(alpha=0.3)

    fig.suptitle("Aedes albopictus -- estadio de huevo (Delatte et al. 2009)",
                 fontsize=13, fontweight="bold")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {out.relative_to(HERE)}")


# ---------------------------------------------------------------------------
# Figura 2: panel comparativo albopictus vs aegypti
# ---------------------------------------------------------------------------

def plot_params_overview(out: Path) -> None:
    T = np.linspace(5, 45, 401)

    fig, axes = plt.subplots(2, 3, figsize=(14, 8.5), constrained_layout=True)

    panels = [
        # (ax, key_alb, key_aeg, title, ylabel)
        (axes[0, 0], "a",    "a",   r"Tasa de mordedura $a_b(T)$",
            r"dia$^{-1}$"),
        (axes[0, 1], "EFOC", "EFD", r"Fecundidad: EFOC$_b$ (alb.) vs EFD (aeg.)",
            r"huevos $\cdot$ unidad$^{-1}$"),
        (axes[0, 2], "MDR",  "MDR", r"Tasa de desarrollo $\mathrm{MDR}_b(T)$",
            r"dia$^{-1}$"),
        (axes[1, 0], "pEA",  "pEA", r"Supervivencia $p_{EAb}(T)$",
            "adim."),
        (axes[1, 1], "lf",   "lf",  r"Longevidad $lf_b(T)$",
            "dias"),
    ]

    for ax, k_alb, k_aeg, title, ylabel in panels:
        y_alb = evaluate(PARAMS_ALBOPICTUS, k_alb, T)
        y_aeg = evaluate(PARAMS_AEGYPTI, k_aeg, T)
        ax.plot(T, y_alb, "-", color="#1f6feb", lw=2.0,
                label=f"albopictus ({k_alb})")
        ax.plot(T, y_aeg, "--", color="#c0392b", lw=1.5,
                label=f"aegypti ({k_aeg})")
        ax.set_xlabel("Temperatura (°C)")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=9, loc="best")

    # Panel 6: phi_{1b} (solo albopictus, requiere combinar EFOC*a y lf)
    ax = axes[1, 2]
    sigma = 1.0
    a_alb = evaluate(PARAMS_ALBOPICTUS, "a", T)
    efoc_alb = evaluate(PARAMS_ALBOPICTUS, "EFOC", T)
    lf_alb = evaluate(PARAMS_ALBOPICTUS, "lf", T)
    mu_F_alb = np.divide(1.0, lf_alb, out=np.full_like(lf_alb, np.nan),
                          where=lf_alb > 0)
    phi_alb = efoc_alb * a_alb
    phi1_alb = np.divide(sigma * phi_alb, mu_F_alb + sigma,
                         out=np.zeros_like(phi_alb),
                         where=np.isfinite(mu_F_alb))
    ax.plot(T, phi1_alb, "-", color="#1f8a3c", lw=2.0,
            label=r"$\phi_{1b}$ (alb.)")
    ax.set_xlabel("Temperatura (°C)")
    ax.set_ylabel(r"$\phi_{1b}$ (huevos $\cdot$ dia$^{-1}$)")
    ax.set_title(r"Reclutamiento efectivo $\phi_{1b}(T)$, $\sigma=1$")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9, loc="best")

    fig.suptitle(
        "Aedes albopictus vs Aedes aegypti -- parametros termicos "
        "(Mordecai et al. 2017, Tabla S1)",
        fontsize=13, fontweight="bold")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {out.relative_to(HERE)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    plot_egg_stage(FIG_DIR / "albopictus_egg_stage.png")
    plot_params_overview(FIG_DIR / "albopictus_params_overview.png")


if __name__ == "__main__":
    main()
