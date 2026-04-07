from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import savemat

from .paths import FULL_TABLE_MAT, ensure_data_dir, find_field_csv


DATE_COLUMN = "Fecha de colecta de ovitrampa"
LOCALITY_COLUMN = "Localidad"
AEG_COLUMN = "Total adultos aedes aegypti"
ALB_COLUMN = "Total adultos aedes albopictus"
HEADER_CODE = "d_dte_clc"


def build_field_table(csv_path=None, output_path=None, locality="LITA"):
    csv_path = Path(csv_path) if csv_path is not None else find_field_csv()
    output_path = Path(output_path) if output_path is not None else FULL_TABLE_MAT

    table_data = pd.read_csv(csv_path)
    table_data = table_data[table_data[DATE_COLUMN] != HEADER_CODE].copy()
    table_data[LOCALITY_COLUMN] = table_data[LOCALITY_COLUMN].astype(str).str.strip()
    table_data = table_data[table_data[LOCALITY_COLUMN].str.upper() == locality.upper()].copy()

    table_data["temp_date"] = pd.to_datetime(
        table_data[DATE_COLUMN],
        format="%m/%d/%y",
        errors="coerce",
    )
    table_data["Num_aeg"] = pd.to_numeric(table_data[AEG_COLUMN], errors="coerce").fillna(0.0)
    table_data["Num_alb"] = pd.to_numeric(table_data[ALB_COLUMN], errors="coerce").fillna(0.0)
    table_data = table_data.dropna(subset=["temp_date"])

    grouped = (
        table_data.groupby("temp_date", as_index=False)[["Num_aeg", "Num_alb"]]
        .sum()
        .sort_values("temp_date")
        .reset_index(drop=True)
    )
    if grouped.empty:
        raise ValueError(
            f"No se encontraron filas validas para la localidad {locality!r} en {csv_path}."
        )

    grouped["Days_Passed"] = (grouped["temp_date"] - grouped["temp_date"].iloc[0]).dt.days + 1

    ensure_data_dir()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    savemat(
        output_path,
        {
            "table_data": {
                "temp_date": grouped["temp_date"].dt.strftime("%Y-%m-%d").to_numpy(dtype=object),
                "Days_Passed": grouped["Days_Passed"].to_numpy(dtype=float),
                "Num_aeg": grouped["Num_aeg"].to_numpy(dtype=float),
                "Num_alb": grouped["Num_alb"].to_numpy(dtype=float),
            }
        },
    )

    return grouped


def main():
    parser = argparse.ArgumentParser(
        description="Reconstruye full_table_Lita.mat a partir del CSV de campo."
    )
    parser.add_argument("--csv-path", type=Path, default=None)
    parser.add_argument("--output-path", type=Path, default=FULL_TABLE_MAT)
    parser.add_argument("--locality", default="LITA")
    args = parser.parse_args()

    grouped = build_field_table(
        csv_path=args.csv_path,
        output_path=args.output_path,
        locality=args.locality,
    )
    print(
        f"Archivo generado: {args.output_path} | filas agregadas: {len(grouped)} | "
        f"rango: {grouped['temp_date'].min().date()} -> {grouped['temp_date'].max().date()}"
    )


if __name__ == "__main__":
    main()
