from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .paths import PARAMS_DATA_DIR


EXPECTED_FILES = {
    "Adult_Lifespan_alb.csv": ("Temperature", "AdultLifespan"),
    "MDR_alb.csv": ("Temperature", "MDR"),
    "Fecundity_alb.csv": ("Temperature", "eggs_per_female_per_cycle"),
    "Biting_rate.csv": ("Temperature", "Biting_rate"),
    "EAS_alb.csv": ("Temperature", "EAS"),
}


def _require_file(data_dir, filename):
    path = data_dir / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Falta {filename} en {data_dir}. Coloca ahi los CSV de literatura para ejecutar params_b_fits."
        )
    return path


def _fit_table(data_dir, filename, x_column, y_column, degree):
    table = pd.read_csv(_require_file(data_dir, filename))
    return np.polyfit(table[x_column], table[y_column], degree), table


def _validate_required_files(data_dir):
    missing = sorted(filename for filename in EXPECTED_FILES if not (data_dir / filename).exists())
    if missing:
        missing_lines = "\n".join(f"- {filename}" for filename in missing)
        raise FileNotFoundError(
            "Faltan CSVs de literatura requeridos para ejecutar params_b_fits en "
            f"{data_dir}:\n{missing_lines}"
        )


def fit_params(data_dir=None, plot=True):
    data_dir = PARAMS_DATA_DIR if data_dir is None else Path(data_dir)
    _validate_required_files(data_dir)

    fit_lifespan, lifespan_table = _fit_table(
        data_dir, "Adult_Lifespan_alb.csv", "Temperature", "AdultLifespan", 5
    )
    fit_dev, dev_table = _fit_table(data_dir, "MDR_alb.csv", "Temperature", "MDR", 6)
    fit_fecund, fecundity_table = _fit_table(
        data_dir, "Fecundity_alb.csv", "Temperature", "eggs_per_female_per_cycle", 6
    )
    fit_br, biting_rate = _fit_table(data_dir, "Biting_rate.csv", "Temperature", "Biting_rate", 6)
    fit_eas, eas_table = _fit_table(data_dir, "EAS_alb.csv", "Temperature", "EAS", 6)

    x_values = np.linspace(10, 35, 40)
    mu_l_b = np.polyval(fit_dev, x_values) / np.polyval(fit_eas, x_values) - np.polyval(
        fit_dev, x_values
    )

    development_time_x = np.array([10, 15, 25, 30], dtype=float)
    development_time_y = np.array([2, 4.5, 7.4, 6.7], dtype=float)
    development_time = np.polyfit(development_time_x, development_time_y, 3)

    egg_l1_x = np.array([10, 15, 25, 30], dtype=float)
    egg_l1_y = np.array([0.04, 0.08, 0.49, 0.51], dtype=float)
    egg_l1 = np.polyfit(egg_l1_x, egg_l1_y, 3)
    psi_1_b = 1.0 / np.polyval(development_time, x_values)
    mu_e_b = psi_1_b / np.polyval(egg_l1, x_values) - psi_1_b

    if plot:
        fig, axes = plt.subplots(2, 3, figsize=(15, 9))
        axes = axes.ravel()

        axes[0].plot(lifespan_table["Temperature"], 1.0 / lifespan_table["AdultLifespan"], "o")
        axes[0].plot(x_values, 1.0 / np.polyval(fit_lifespan, x_values), "-")
        axes[0].set_title("mu_F_b")

        axes[1].plot(dev_table["Temperature"], dev_table["MDR"], "o")
        axes[1].plot(x_values, np.polyval(fit_dev, x_values), "-")
        axes[1].set_title("psi_2_b")

        axes[2].plot(eas_table["Temperature"], eas_table["EAS"], "o")
        axes[2].plot(x_values, mu_l_b, "-")
        axes[2].set_title("mu_L_b")

        axes[3].plot(fecundity_table["Temperature"], fecundity_table["eggs_per_female_per_cycle"], "o")
        axes[3].plot(x_values, np.polyval(fit_fecund, x_values), "-")
        axes[3].set_title("fecundity")

        axes[4].plot(biting_rate["Temperature"], biting_rate["Biting_rate"], "o")
        axes[4].plot(x_values, np.polyval(fit_br, x_values), "-")
        axes[4].set_title("biting_rate")

        axes[5].plot(x_values, mu_e_b, "-")
        axes[5].set_title("mu_E_b")

        for ax in axes:
            ax.grid(True)
        fig.tight_layout()

    return {
        "mu_F_b": fit_lifespan,
        "psi_2_b": fit_dev,
        "phi_B_fecundity": fit_fecund,
        "phi_B_biting_rate": fit_br,
        "mu_L_b_eas": fit_eas,
        "psi_1_b_development_time": development_time,
        "mu_E_b_egg_l1": egg_l1,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Recalcula ajustes polinomiales auxiliares para albopictus."
    )
    parser.add_argument("--data-dir", type=Path, default=PARAMS_DATA_DIR)
    parser.add_argument("--no-plot", action="store_true")
    args = parser.parse_args()

    try:
        fits = fit_params(data_dir=args.data_dir, plot=not args.no_plot)
    except FileNotFoundError as exc:
        print(exc)
        return

    for name, coeffs in fits.items():
        print(f"{name}: {coeffs}")

    if not args.no_plot:
        plt.show()


if __name__ == "__main__":
    main()
