"""Test de regresión contra el snapshot guardado del modelo Python.

El snapshot `data/python_snapshot.json` captura el output esperado con la
config por defecto. Este test detecta si cambios en el código alteran
(intencionalmente o no) el resultado numérico del modelo.

Si el cambio es intencional, regenerar el snapshot con:
    python -m dengue_model.diagnostics --snapshot
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from dengue_model import ModelConfig, run_elf, set_config
from dengue_model.paths import DATA_DIR


SNAPSHOT_PATH = DATA_DIR / "python_snapshot.json"
RTOL = 1e-8  # RK45 es determinista con los mismos inputs


@pytest.mark.skipif(
    not SNAPSHOT_PATH.exists(),
    reason="Snapshot no existe; generar con 'python -m dengue_model.diagnostics --snapshot'",
)
def test_matches_snapshot():
    with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
        snap = json.load(f)

    # Aplicar la config del snapshot (por si cambiaron defaults después de guardarlo)
    set_config(ModelConfig.from_dict(snap["config"]))
    try:
        result = run_elf(plot=False)

        t_snap = np.asarray(snap["t"])
        y_snap = np.asarray(snap["y"])

        np.testing.assert_allclose(result["t"], t_snap, rtol=RTOL, atol=1e-10,
                                    err_msg="t divergió del snapshot")
        np.testing.assert_allclose(result["y"], y_snap, rtol=RTOL, atol=1e-6,
                                    err_msg="y divergió del snapshot")
    finally:
        set_config(ModelConfig())
