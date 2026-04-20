from __future__ import annotations

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat

from . import config
from ._utils import safe_fraction
from .figure_setups import setup
from .myODE_ELF import solve_model
from .my_parameters import equilibrium_a
from .paths import FULL_TABLE_MAT
from .time_col_date import build_field_table


@dataclass
class FieldData:
    temp_date: np.ndarray
    days_passed: np.ndarray
    num_aeg: np.ndarray
    num_alb: np.ndarray


def _load_table_struct(mat_path):
    raw = loadmat(mat_path, squeeze_me=True, struct_as_record=False)
    table_data = raw["table_data"]
    return table_data


def load_field_data(mat_path=None, rebuild_if_missing=True):
    mat_path = FULL_TABLE_MAT if mat_path is None else mat_path
    if rebuild_if_missing and not mat_path.exists():
        build_field_table(output_path=mat_path)

    table_data = _load_table_struct(mat_path)
    return FieldData(
        temp_date=np.atleast_1d(np.asarray(table_data.temp_date)),
        days_passed=np.atleast_1d(np.asarray(table_data.Days_Passed, dtype=float)),
        num_aeg=np.atleast_1d(np.asarray(table_data.Num_aeg, dtype=float)),
        num_alb=np.atleast_1d(np.asarray(table_data.Num_alb, dtype=float)),
    )


def simulate_segments(p, data):
    intro_day = config.CONFIG.albopictus_introduction_day
    ea0, la0, fa0 = equilibrium_a()
    y01 = np.array([ea0, la0, fa0, 0.0, 0.0, 0.0], dtype=float)

    tspan1 = np.arange(0.0, intro_day + 1.0, 1.0)
    t1, y1 = solve_model(t_eval=tspan1, y0=y01, p=p)

    final_day = max(float(np.ceil(data.days_passed[-1])), intro_day)
    if final_day <= intro_day:
        return t1, y1

    tspan2 = np.arange(intro_day, final_day + 1.0, 1.0)
    # Inyección inicial de albopictus al segundo segmento
    y02 = np.array(
        [y1[-1, 0], y1[-1, 1], y1[-1, 2], 0.0, 0.0, 1.0],
        dtype=float,
    )
    t2, y2 = solve_model(t_eval=tspan2, y0=y02, p=p)

    t = np.concatenate([t1, t2[1:]])
    y = np.vstack([y1, y2[1:]])
    return t, y


def _plot_fractions(t, y):
    ae_tot_a = y[:, 0] + y[:, 1] + y[:, 2]
    ae_tot_b = y[:, 3] + y[:, 4] + y[:, 5]
    fractions = np.column_stack(
        [
            safe_fraction(y[:, 0], ae_tot_a),
            safe_fraction(y[:, 1], ae_tot_a),
            safe_fraction(y[:, 2], ae_tot_a),
            safe_fraction(y[:, 3], ae_tot_b),
            safe_fraction(y[:, 4], ae_tot_b),
            safe_fraction(y[:, 5], ae_tot_b),
        ]
    )

    labels = ["Ea frac", "La frac", "Fa frac", "Eb frac", "Lb frac", "Fb frac"]
    styles = ["r-", "g--", "b-.", "c-", "m--", "y-."]

    fig, ax = setup()
    for idx, (label, style) in enumerate(zip(labels, styles)):
        ax.plot(t, fractions[:, idx], style, label=label)
    ax.set_xlabel("t")
    ax.legend()
    fig.tight_layout()

    intro_day = config.CONFIG.albopictus_introduction_day
    fig_zoom, ax_zoom = setup()
    mask = (t >= intro_day - 17) & (t <= intro_day + 45)
    for idx, (label, style) in enumerate(zip(labels, styles)):
        ax_zoom.plot(t[mask], fractions[mask, idx], style, label=label)
    ax_zoom.set_xlabel("t")
    ax_zoom.set_title(f"Zoom alrededor de introducción albopictus (t={intro_day})")
    ax_zoom.legend()
    fig_zoom.tight_layout()


def error_fun_betas(p, data=None, plot=False, verbose=False, return_details=False):
    p = np.asarray(p, dtype=float)
    data = load_field_data() if data is None else data
    t, y = simulate_segments(p, data)

    y_interp_aeg = np.interp(data.days_passed, t, y[:, 1])
    y_interp_alb = np.interp(data.days_passed, t, y[:, 4])

    err1 = float(np.square(y_interp_aeg - data.num_aeg).sum())
    err2 = float(np.square(y_interp_alb - data.num_alb).sum())
    total_error = err1 + err2

    if verbose:
        print(f"betas={p.tolist()} err_aeg={err1:.6f} err_alb={err2:.6f} total={total_error:.6f}")

    if plot:
        _plot_fractions(t, y)
        plt.show()

    if return_details:
        return {
            "error": total_error,
            "err_aeg": err1,
            "err_alb": err2,
            "t": t,
            "y": y,
            "y_interp_aeg": y_interp_aeg,
            "y_interp_alb": y_interp_alb,
        }

    return total_error
