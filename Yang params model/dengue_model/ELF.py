from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np

from ._utils import safe_fraction
from .figure_setups import setup
from .myODE_ELF import solve_model
from .my_parameters import DEFAULT_COMPETITION, initial_state


def compartment_fractions(y):
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


def run_elf(tfinal=365.0, num_points=100, competition=None, plot=True):
    if competition is None:
        competition = DEFAULT_COMPETITION

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
        ax.set_xlabel("t")
        ax.set_ylabel("Fraccion del compartimento")
        ax.legend()
        fig.tight_layout()

    return {"t": t, "y": y, "fractions": fractions}


def main():
    parser = argparse.ArgumentParser(description="Ejecuta la simulacion principal ELF.")
    parser.add_argument("--tfinal", type=float, default=365.0)
    parser.add_argument("--num-points", type=int, default=100)
    parser.add_argument("--beta-ba", type=float, default=float(DEFAULT_COMPETITION[0]))
    parser.add_argument("--beta-ab", type=float, default=float(DEFAULT_COMPETITION[1]))
    parser.add_argument("--no-plot", action="store_true")
    args = parser.parse_args()

    competition = np.array([args.beta_ba, args.beta_ab], dtype=float)
    run_elf(
        tfinal=args.tfinal,
        num_points=args.num_points,
        competition=competition,
        plot=not args.no_plot,
    )

    if not args.no_plot:
        plt.show()


if __name__ == "__main__":
    main()
