# Analisis MATLAB vs Python

## Resumen

La migracion cubre todos los modulos `.m` relevantes del modelo original y agrega utilidades Python para rutas y manejo numerico seguro.

## Cobertura de archivos

| MATLAB | Python | Estado |
|---|---|---|
| `ELF.m` | `ELF.py` | Migrado |
| `myODE_ELF.m` | `myODE_ELF.py` | Migrado |
| `my_parameters.m` | `my_parameters.py` | Migrado |
| `error_fun_betas.m` | `error_fun_betas.py` | Migrado y corregido |
| `time_col_date.m` | `time_col_date.py` | Migrado y redisenado |
| `params_b_fits.m` | `params_b_fits.py` | Migrado y desacoplado de rutas absolutas |
| `figure_setups.m` | `figure_setups.py` | Migrado en version minima |
| `temp.m` | `temp.py` | Migrado |
| `phi_A.m` / `phi_B.m` | `phi_A.py` / `phi_B.py` | Migrado |
| `phi_p_a.m` / `phi_p_b.m` | `phi_p_a.py` / `phi_p_b.py` | Migrado |
| `psi1_a.m` / `psi1_b.m` | `psi1_a.py` / `psi1_b.py` | Migrado |
| `psi2_a.m` / `psi2_b.m` | `psi2_a.py` / `psi2_b.py` | Migrado |
| `muE_a.m` / `muE_b.m` | `muE_a.py` / `muE_b.py` | Migrado |
| `muF_a.m` / `muF_b.m` | `muF_a.py` / `muF_b.py` | Migrado |
| `muL_a.m` / `muL_b.m` | `muL_a.py` / `muL_b.py` | Migrado |

## Modulos solo Python

- `paths.py`: centraliza rutas del paquete y datos.
- `_utils.py`: utilidades numericas y compatibilidad escalar/vector.

## Diferencias funcionales importantes

### 1. Paso del vector de competencia

- MATLAB tiene una inconsistencia entre `ELF.m` y `myODE_ELF.m`: el script llama `myODE_ELF(t,y)` pero la funcion recibe `myODE_ELF(t,y,p)`.
- Python resuelve esto con `DEFAULT_COMPETITION = [0.5, 0.5]` y paso explicito de `p`.

### 2. Integracion numerica

- MATLAB usa `ode45`.
- Python usa `scipy.integrate.solve_ivp(..., method='RK45')`.
- La formulacion es equivalente, pero no se garantiza igualdad numerica exacta punto a punto.

### 3. Funcion de error

- MATLAB referencia `tspan` en `interp1` aunque el vector concatenado correcto es `t`.
- Python interpola contra `t` y suma el error de ambas especies.

### 4. Preprocesado de datos de campo

- MATLAB depende de una ruta fija y de un CSV sin limpieza adicional.
- Python limpia la fila de codigos de variable, normaliza la localidad `LITA`, agrega por fecha y genera `full_table_Lita.mat`.

### 5. Ajustes de literatura

- MATLAB depende de CSVs externos con rutas absolutas y contiene una referencia incompleta a `survival_rate`.
- Python usa `params_b_fits.py` con rutas configurables y depende de CSVs explicitos en `data/params_literature`.

## Huecos del MATLAB original detectados

- `ELF.m` no pasa `p` a `myODE_ELF`.
- `error_fun_betas.m` usa `tspan` no definido.
- `time_col_date.m` llama `error_fun_betas(p, data)` aunque `error_fun_betas.m` no acepta ese segundo argumento.
- `params_b_fits.m` no es portable y contiene referencias incompletas.

## Estado actual

- La simulacion principal Python corre.
- La reconstruccion de `full_table_Lita.mat` corre.
- La funcion de error para betas corre.
- `params_b_fits.py` queda operativo con los CSVs ya presentes en `data/params_literature`.
