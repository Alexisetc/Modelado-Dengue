"""Herramientas de diagnóstico del modelo ELF.

Comandos:
    python -m dengue_model.diagnostics --plot-rates
        Barrido de las 14 funciones biológicas sobre T ∈ [15, 40] °C,
        guardado como PNG y CSV en `data/diagnostics/`.

    python -m dengue_model.diagnostics --snapshot
        Guarda el output actual de run_elf() como `data/python_snapshot.json`
        para usar como baseline de regresión (detectar cambios no intencionados).

    python -m dengue_model.diagnostics --compare-snapshot
        Compara el output actual contra `python_snapshot.json` y reporta
        desviaciones por compartimento.

    python -m dengue_model.diagnostics --save-figure <ruta>
        Corre la simulación y guarda la figura principal de fracciones.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from . import config
from .ELF import compare_against_baseline, compartment_fractions, run_elf
from .figure_setups import setup
from .paths import DATA_DIR
from .temp import temp


# ---------------------------------------------------------------------------
# Barrido de tasas biológicas por temperatura
# ---------------------------------------------------------------------------

def _rate_table(t_grid):
    """Evalúa cada función biológica directamente en una grilla de T (°C).

    Las funciones del paquete toman `day` y derivan T vía `temp(day)`, pero
    `temp()` solo cubre un rango estrecho (~24–27°C con defaults). Para
    diagnóstico necesitamos evaluar los polinomios fuera de ese rango, así
    que reimplementamos inline la evaluación directa en T.
    """
    from . import muE_a as _mea
    from . import muE_b as _meb
    from . import muF_a as _mfa
    from . import muF_b as _mfb
    from . import muL_a as _mla
    from . import muL_b as _mlb
    from . import phi_A as _pha
    from . import phi_B as _phb
    from . import psi1_a as _p1a
    from . import psi1_b as _p1b
    from . import psi2_a as _p2a
    from . import psi2_b as _p2b

    # Aplicamos el mismo clipping que las funciones "reales"
    cfg = config.CONFIG
    T = np.clip(t_grid, cfg.poly_temp_min, cfg.poly_temp_max)

    # Evaluaciones directas (replica la lógica interna de cada módulo)
    phi_A = np.polyval(_pha.COEFFICIENTS, T)
    phi_B = np.polyval(_phb.COEFF_BR, T) * np.polyval(_phb.COEFF_FECUND, T)

    psi1_b = np.polyval(_p1b.COEFFICIENTS, T)
    psi2_a = np.polyval(_p2a.COEFFICIENTS, T)
    psi2_b = np.polyval(_p2b.COEFFICIENTS, T)

    # muE_a: 1 / polinomio (con floor)
    muE_a_raw = np.polyval(_mea.COEFFICIENTS, T)
    muE_a = 1.0 / np.clip(muE_a_raw, _mea._LIFETIME_FLOOR, None)

    # muF_a: polinomio directo
    muF_a = np.polyval(_mfa.COEFFICIENTS, T)

    # muF_b: 1 / polinomio
    muF_b_raw = np.polyval(_mfb.COEFFICIENTS, T)
    muF_b = 1.0 / np.clip(muF_b_raw, _mfb._LIFETIME_FLOOR, None)

    # muL_a: polinomio directo
    muL_a = np.polyval(_mla.COEFFICIENTS, T)

    # muE_b: dev_rate / egg_l1 − dev_rate
    dev_rate = np.polyval(_meb.DEV_RATE_COEFFS, T)
    egg_l1 = np.clip(np.polyval(_meb.EGG_L1_COEFFS, T), _meb._EGG_L1_FLOOR, None)
    muE_b = dev_rate / egg_l1 - dev_rate

    # muL_b: psi_2b / eas − psi_2b
    psi_2b_raw = np.polyval(_mlb.PSI_2B_COEFFS, T)
    eas = np.clip(np.polyval(_mlb.EAS_COEFFS, T), _mlb._EAS_FLOOR, None)
    muL_b = psi_2b_raw / eas - psi_2b_raw

    # psi1_a: (mu_E_a · EP) / (1 − EP) con EP clippeado
    ep_raw = np.polyval(_p1a.POLYFIT, T)
    ep = np.clip(ep_raw, 0.0, 0.999)
    psi1_a = (muE_a * ep) / (1.0 - ep)

    # phi_p_a y phi_p_b: las tasas efectivas usan las mortalidades BASE
    # (no las ajustadas por el multiplicador — así están definidas en phi_p_a.py)
    phi_p_a = (phi_A * cfg.sigma_aegypti) / (muF_a + cfg.sigma_aegypti)
    phi_p_b = (phi_B * cfg.sigma_albopictus) / (muF_b + cfg.sigma_albopictus)

    result = {
        "T_C":     t_grid.tolist(),
        "phi_A":   phi_A.tolist(),
        "phi_B":   phi_B.tolist(),
        "phi_p_a": phi_p_a.tolist(),
        "phi_p_b": phi_p_b.tolist(),
        "psi1_a":  psi1_a.tolist(),
        "psi1_b":  psi1_b.tolist(),
        "psi2_a":  psi2_a.tolist(),
        "psi2_b":  psi2_b.tolist(),
        "muE_a":   muE_a.tolist(),
        "muE_b":   muE_b.tolist(),
        "muL_a":   muL_a.tolist(),
        "muL_b":   muL_b.tolist(),
        "muF_a":   muF_a.tolist(),
        "muF_b":   muF_b.tolist(),
    }
    return result


def plot_rates(output_dir: Path | None = None):
    """Grafica las 14 tasas biológicas en T ∈ [min, max] y exporta CSV+PNG."""
    import csv

    cfg = config.CONFIG
    output_dir = output_dir or (DATA_DIR / "diagnostics")
    output_dir.mkdir(parents=True, exist_ok=True)

    t_grid = np.linspace(cfg.poly_temp_min, cfg.poly_temp_max, 50)
    table = _rate_table(t_grid)

    # CSV
    csv_path = output_dir / "rates_vs_temperature.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(list(table.keys()))
        rows = zip(*table.values())
        writer.writerows(rows)
    print(f"[diagnostics] CSV guardado: {csv_path}")

    # Plot: 7 subplots (uno por categoría de tasa), especies superpuestas
    groups = [
        ("Fecundidad base",       "phi_A",   "phi_B"),
        ("Oviposición efectiva",  "phi_p_a", "phi_p_b"),
        ("Desarrollo huevo→larva", "psi1_a",  "psi1_b"),
        ("Desarrollo larva→adulto","psi2_a",  "psi2_b"),
        ("Mortalidad huevo",       "muE_a",   "muE_b"),
        ("Mortalidad larva",       "muL_a",   "muL_b"),
        ("Mortalidad adulto",      "muF_a",   "muF_b"),
    ]

    fig, axes = plt.subplots(4, 2, figsize=(12, 14))
    axes_flat = axes.flatten()
    for ax, (title, fa, fb) in zip(axes_flat, groups):
        ax.plot(t_grid, table[fa], "b-", label=fa + " (aegypti)", linewidth=2)
        ax.plot(t_grid, table[fb], "r--", label=fb + " (albopictus)", linewidth=2)
        ax.set_xlabel("T (°C)")
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    # Último axis vacío
    axes_flat[-1].axis("off")
    fig.suptitle("Tasas biológicas vs temperatura", fontsize=14, y=1.00)
    fig.tight_layout()

    png_path = output_dir / "rates_vs_temperature.png"
    fig.savefig(png_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[diagnostics] PNG guardado: {png_path}")

    return csv_path, png_path


# ---------------------------------------------------------------------------
# Snapshot del output del modelo (baseline de regresión)
# ---------------------------------------------------------------------------

SNAPSHOT_PATH = DATA_DIR / "python_snapshot.json"


def save_snapshot(path: Path | None = None):
    path = path or SNAPSHOT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    result = run_elf(plot=False)
    payload = {
        "config": config.CONFIG.to_dict(),
        "t": result["t"].tolist(),
        "y": result["y"].tolist(),
        "fractions": result["fractions"].tolist(),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"[diagnostics] Snapshot guardado: {path}")
    print(f"[diagnostics] y0 = {result['y'][0].tolist()}")
    print(f"[diagnostics] y_final = {result['y'][-1].tolist()}")
    return path


def compare_snapshot(path: Path | None = None, rtol: float = 1e-4):
    path = path or SNAPSHOT_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"No existe snapshot en {path}. Genera uno con --snapshot primero."
        )
    result = run_elf(plot=False)
    report = compare_against_baseline(result, path)

    print(f"\n=== Comparación contra snapshot Python ({path.name}) ===")
    print(f"{'Comp':<6} {'max_abs':>12} {'mean_abs':>12} {'max_rel':>10} {'worst_t':>10}")
    any_fail = False
    for name, m in report.items():
        failed = m["max_rel_diff"] > rtol
        any_fail = any_fail or failed
        flag = "  !!" if failed else ""
        print(
            f"{name:<6} {m['max_abs_diff']:>12.4e} {m['mean_abs_diff']:>12.4e} "
            f"{m['max_rel_diff']:>10.2%} {m['worst_t']:>10.1f}{flag}"
        )

    if any_fail:
        print(f"\n[WARN] Algunas desviaciones exceden rtol={rtol}. Regresión detectada.")
    else:
        print(f"\n[OK] Todas las desviaciones dentro de rtol={rtol}.")
    return report


# ---------------------------------------------------------------------------
# Figura del modelo (PNG)
# ---------------------------------------------------------------------------

def save_figure(path: Path):
    """Corre la simulación y guarda la figura de fracciones en `path`."""
    result = run_elf(plot=False)
    t = result["t"]
    fractions = result["fractions"]

    fig, ax = setup()
    labels = ["Ea frac", "La frac", "Fa frac", "Eb frac", "Lb frac", "Fb frac"]
    styles = ["r-", "g--", "b-.", "c-", "m--", "y-."]
    for idx, (label, style) in enumerate(zip(labels, styles)):
        ax.plot(t, fractions[:, idx], style, label=label)
    ax.set_xlabel("t (días)")
    ax.set_ylabel("Fracción del compartimento")
    ax.set_title("ELF — dinámica poblacional (config defaults)")
    ax.legend()
    fig.tight_layout()

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[diagnostics] Figura guardada: {path}")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Diagnósticos del modelo ELF.")
    parser.add_argument("--plot-rates", action="store_true",
                        help="Barrido de tasas biológicas vs T, guarda CSV+PNG.")
    parser.add_argument("--snapshot", action="store_true",
                        help="Guarda el output actual como baseline de regresión.")
    parser.add_argument("--compare-snapshot", action="store_true",
                        help="Compara contra el snapshot guardado previamente.")
    parser.add_argument("--save-figure", type=Path, default=None,
                        help="Guarda la figura principal de fracciones en PATH.")
    parser.add_argument("--rtol", type=float, default=1e-4,
                        help="Tolerancia relativa para --compare-snapshot.")
    args = parser.parse_args()

    did_something = False
    if args.plot_rates:
        plot_rates()
        did_something = True
    if args.snapshot:
        save_snapshot()
        did_something = True
    if args.compare_snapshot:
        compare_snapshot(rtol=args.rtol)
        did_something = True
    if args.save_figure is not None:
        save_figure(args.save_figure)
        did_something = True

    if not did_something:
        parser.print_help()


if __name__ == "__main__":
    main()
