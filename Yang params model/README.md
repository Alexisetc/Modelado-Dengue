# Yang Params Model

Migracion operativa del modelo ELF de dengue desde MATLAB a Python, manteniendo la estructura original por modulo y corrigiendo errores heredados del codigo fuente.

## Estructura actual

```text
Yang params model/
|-- README.md
|-- MATLAB_VS_PYTHON_ANALYSIS.md
|-- data/
|   |-- full_table_Lita.mat
|   `-- params_literature/
|       |-- Adult_Lifespan_alb.csv
|       |-- Biting_rate.csv
|       |-- EAS_alb.csv
|       |-- Fecundity_alb.csv
|       `-- MDR_alb.csv
|-- dengue_model/
|   |-- __init__.py
|   |-- ELF.py
|   |-- error_fun_betas.py
|   |-- figure_setups.py
|   |-- myODE_ELF.py
|   |-- my_parameters.py
|   |-- params_b_fits.py
|   |-- paths.py
|   |-- time_col_date.py
|   |-- temp.py
|   |-- phi_A.py
|   |-- phi_B.py
|   |-- phi_p_a.py
|   |-- phi_p_b.py
|   |-- psi1_a.py
|   |-- psi1_b.py
|   |-- psi2_a.py
|   |-- psi2_b.py
|   |-- muE_a.py
|   |-- muE_b.py
|   |-- muF_a.py
|   |-- muF_b.py
|   |-- muL_a.py
|   |-- muL_b.py
|   `-- _utils.py
`-- Yang params model/
    |-- ELF.m
    |-- error_fun_betas.m
    |-- figure_setups.m
    |-- myODE_ELF.m
    |-- my_parameters.m
    |-- params_b_fits.m
    |-- time_col_date.m
    |-- temp.m
    |-- phi_A.m
    |-- phi_B.m
    |-- phi_p_a.m
    |-- phi_p_b.m
    |-- psi1_a.m
    |-- psi1_b.m
    |-- psi2_a.m
    |-- psi2_b.m
    |-- muE_a.m
    |-- muE_b.m
    |-- muF_a.m
    |-- muF_b.m
    |-- muL_a.m
    `-- muL_b.m
```

## Carpetas principales

- `dengue_model`: implementacion Python del modelo.
- `data`: datos generados y tablas auxiliares para calibracion.
- `Yang params model`: fuentes MATLAB originales usadas como referencia.

## Flujo recomendado

1. Regenerar o validar el dataset de campo:
   `python -m dengue_model.time_col_date`
2. Ejecutar la simulacion principal:
   `python -m dengue_model.ELF --no-plot`
3. Evaluar la funcion objetivo del ajuste:
   `python -c "from dengue_model.error_fun_betas import error_fun_betas; print(error_fun_betas([0.5, 0.5]))"`
4. Revisar las tablas de literatura ya incluidas y recalcular ajustes:
   `python -m dengue_model.params_b_fits --no-plot`

## Modulos clave

- `my_parameters.py`: reemplaza `global P` por un objeto central con parametros y funciones dependientes del tiempo.
- `myODE_ELF.py`: sistema ODE de 6 compartimentos.
- `ELF.py`: punto de entrada principal para simulacion.
- `time_col_date.py`: limpia el CSV de campo, normaliza `LITA`, agrega por fecha y genera `full_table_Lita.mat`.
- `error_fun_betas.py`: une simulacion, interpolacion contra datos y error SSE para ambas especies.
- `params_b_fits.py`: recalcula ajustes auxiliares de albopictus a partir de CSVs de literatura explicitamente presentes en `data/params_literature`.

## Datos usados

- CSV de campo localizado automaticamente desde:
  `Data Mosquitoes/Data Mosquitoes/Scripts/INSPI_CZ9_GIDi_SIT_RLA5074_Field_2018-2019-2020-2021_20230503_DC_CM_FM_XAG.csv`
- MAT generado:
  `data/full_table_Lita.mat`
- CSVs de literatura esperados por `params_b_fits`:
  `data/params_literature/*.csv`
- Los CSVs de `params_literature` deben mantenerse como insumos trazables del proyecto. Si cambian, deben actualizarse explicitamente y no se regeneran de forma automatica desde el codigo.

## Diferencias importantes frente a MATLAB

- `solve_ivp` reemplaza `ode45`.
- `error_fun_betas.py` corrige el bug de `tspan` no definido.
- El error total del ajuste suma `aegypti` y `albopictus`.
- `params_b_fits.py` ya no depende de rutas absolutas de macOS.
- `params_b_fits.py` falla de forma explicita si faltan CSVs de literatura requeridos.

## Dependencias

- `numpy`
- `scipy`
- `matplotlib`
- `pandas`

Instalacion sugerida:

```bash
pip install numpy scipy matplotlib pandas
```
