from __future__ import annotations

import matplotlib.pyplot as plt


def setup(figsize=(9, 7)):
    plt.rcParams.update(
        {
            "lines.linewidth": 3,
            "font.size": 14,
            "axes.titlesize": 14,
            "axes.labelsize": 14,
            "legend.fontsize": 12,
            "lines.markersize": 8,
        }
    )
    fig, ax = plt.subplots(figsize=figsize)
    ax.grid(True)
    return fig, ax
