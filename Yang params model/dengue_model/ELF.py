"""Simulación principal del modelo ELF de dengue.

Ejecuta el ODE de 6 compartimentos (3 etapas × 2 especies) sobre un año
y retorna tiempo, estado completo y fracciones por compartimento.

Uso básico:
    python -m dengue_model.ELF                          # defaults
    python -m dengue_model.ELF --no-plot                # sin gráficas
    python -m dengue_model.ELF --config cfg.json        # config externa
    python -m dengue_model.ELF --compare-baseline b.json # validación vs MATLAB
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from . import config
from ._utils import safe_fraction
from .figure_setups import setup
from .myODE_ELF import solve_model
from .my_parameters import default_competition, initial_state


def compartment_fractions(y):
    """Normaliza cada estado por el total de su especie. Devuelve (N, 6)."""
    ae_tot_a = y[:, 0] + y[:, 1] + y[:, 2]
    ae_tot_b = y[:, 3] + y[:, 4] + y[:, 5]
    return np.column_stack(
        [
            safe_fraction(y[:, 0], ae_tot_a),
            safe_fraction(y[:, 1], ae_tot_a),
            safe_fraction(y[:, 2], ae_tot_a),
            safe_fraction(y[:, 3], ae_tot_b),
            safe_fraction(y[:, 4], ae_tot_b),
            safe_fraction(y[:, 5], ae_tot_b),
        ]
    )


def run_elf(tfinal=None, num_points=None, competition=None, plot=True):
    """Corre la simulación ELF y devuelve t, y y fracciones.

    Si algún argumento es None se toma de `config.CONFIG`.
    """
    cfg = config.CONFIG
    if tfinal is None:
        tfinal = cfg.simulation_days
    if num_points is None:
        num_points = cfg.num_points
    if competition is None:
        competition = default_competition()

    y0 = initial_state()
    t_eval = np.linspace(0.0, tfinal, int(num_points))
    t, y = solve_model(t_eval=t_eval, y0=y0, p=competition)
    fractions = compartment_fractions(y)

    if plot:
        fig, ax = setup()
        labels = ["Ea frac", "La frac", "Fa frac", "Eb frac", "Lb frac", "Fb frac"]
        styles = ["r-", "g--", "b-.", "c-", "m--", "y-."]
        for idx, (label, style) in enumerate(zip(labels, styles)):
            ax.plot(t, fractions[:, idx], style, label=label)
        ax.set_xlabel("t (días)")
        ax.set_ylabel("Fracción del compartimento")
        ax.set_title("ELF — dinámica poblacional (fracciones)")
        ax.legend()
        fig.tight_layout()

    return {"t": t, "y": y, "fractions": fractions}


def compare_against_baseline(result: dict, baseline_path: Path) -> dict:
    """Compara el resultado actual contra un baseline JSON exportado desde MATLAB.

    El baseline debe tener keys `t` (lista) y `y` (lista de listas, shape N×6).
    Retorna diccionario con métricas por compartimento.
    """
    with open(baseline_path, "r", encoding="utf-8") as f:
        baseline = json.load(f)

    t_ref = np.asarray(baseline["t"], dtype=float)
    y_ref = np.asarray(baseline["y"], dtype=float)

    t_cur = result["t"]
    y_cur = result["y"]

    # Interpolar current en la grilla del baseline para comparar
    y_cur_interp = np.column_stack(
        [np.interp(t_ref, t_cur, y_cur[:, i]) for i in range(y_cur.shape[1])]
    )
    diff = y_cur_interp - y_ref

    comp_names = ["E_a", "L_a", "F_a", "E_b", "L_b", "F_b"]
    report = {}
    for i, name in enumerate(comp_names):
        abs_diff = np.abs(diff[:, i])
        scale = max(float(np.max(np.abs(y_ref[:, i]))), 1e-12)
        rel = abs_diff / scale
        report[name] = {
            "max_abs_diff": float(np.max(abs_diff)),
            "mean_abs_diff": float(np.mean(abs_diff)),
            "max_rel_diff": float(np.max(rel)),
            "worst_t": float(t_ref[int(np.argmax(abs_diff))]),
        }
    return report


def _print_baseline_report(report: dict) -> None:
    print("\n=== Comparación contra baseline MATLAB ===")
    print(f"{'Comp':<6} {'max_abs':>12} {'mean_abs':>12} {'max_rel':>10} {'worst_t':>10}")
    for name, m in report.items():
        flag = "  !!" if m["max_rel_diff"] > 0.01 else ""
        print(
            f"{name:<6} {m['max_abs_diff']:>12.4e} {m['mean_abs_diff']:>12.4e} "
            f"{m['max_rel_diff']:>10.2%} {m['worst_t']:>10.1f}{flag}"
        )


def main():
    parser = argparse.ArgumentParser(description="Ejecuta la simulación principal ELF.")
    parser.add_argument("--tfinal", type=float, default=None,
                        help="Días totales a simular (default: config.simulation_days).")
    parser.add_argument("--num-points", type=int, default=None,
                        help="Puntos de output (default: config.num_points).")
    parser.add_argument("--beta-ba", type=float, default=None,
                        help="Competencia de albopictus sobre aegypti (default: config.beta_ba).")
    parser.add_argument("--beta-ab", type=float, default=None,
                        help="Competencia de aegypti sobre albopictus (default: config.beta_ab).")
    parser.add_argument("--config", type=Path, default=None,
                        help="Ruta a JSON con ModelConfig override.")
    parser.add_argument("--compare-baseline", type=Path, default=None,
                        help="Ruta a baseline.json (output MATLAB) para comparar.")
    parser.add_argument("--no-plot", action="store_true")
    args = parser.parse_args()

    if args.config is not None:
        cfg = config.ModelConfig.from_json(args.config)
        config.set_config(cfg)
        print(f"[config] cargado desde {args.config}")

    beta_ba = args.beta_ba if args.beta_ba is not None else config.CONFIG.beta_ba
    beta_ab = args.beta_ab if args.beta_ab is not None else config.CONFIG.beta_ab
    competition = np.array([beta_ba, beta_ab], dtype=float)

    result = run_elf(
        tfinal=args.tfinal,
        num_points=args.num_points,
        competition=competition,
        plot=not args.no_plot,
    )

    print(f"[run_elf] t: shape={result['t'].shape}, y: shape={result['y'].shape}")
    print(f"[run_elf] y0={result['y'][0].tolist()}")
    print(f"[run_elf] y_final={result['y'][-1].tolist()}")

    if args.compare_baseline is not None:
        report = compare_against_baseline(result, args.compare_baseline)
        _print_baseline_report(report)

    if not args.no_plot:
        plt.show()


if __name__ == "__main__":
    main()
