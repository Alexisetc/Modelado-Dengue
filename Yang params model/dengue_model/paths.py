from __future__ import annotations

from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
MODEL_ROOT = PACKAGE_DIR.parent
REPO_ROOT = MODEL_ROOT.parent
DATA_DIR = MODEL_ROOT / "data"
PARAMS_DATA_DIR = DATA_DIR / "params_literature"
FULL_TABLE_MAT = DATA_DIR / "full_table_Lita.mat"

_RAW_FIELD_CSV_CANDIDATES = [
    REPO_ROOT
    / "Data Mosquitoes"
    / "Scripts"
    / "INSPI_CZ9_GIDi_SIT_RLA5074_Field_2018-2019-2020-2021_20230503_DC_CM_FM_XAG.csv",
]


def ensure_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def find_field_csv() -> Path:
    for candidate in _RAW_FIELD_CSV_CANDIDATES:
        if candidate.exists():
            return candidate

    for candidate in REPO_ROOT.rglob("*.csv"):
        if "Field" in candidate.name and "INSPI_CZ9" in candidate.name:
            return candidate

    raise FileNotFoundError(
        "No se encontro el CSV de campo esperado para reconstruir full_table_Lita."
    )
