# Yang Params Model — Modelo ELF de Dengue

Modelo dinámico de competencia entre *Aedes aegypti* y *Aedes albopictus* con 6 compartimentos ODE (huevo / larva / adulto × 2 especies) y tasas biológicas dependientes de temperatura. Migración de MATLAB → Python con corrección de bugs heredados, configuración centralizada y validación automática.

## Estructura de esta carpeta

```
Yang params model/
├── README.md                         ← este archivo
├── dengue_model/                     ← código Python del modelo
├── tests/                            ← suite de validación automática
├── data/                             ← datos e insumos
│   ├── full_table_Lita.mat          (datos de campo procesados)
│   ├── params_literature/           (CSVs de la literatura)
│   ├── python_snapshot.json         (baseline numérico de regresión)
│   └── diagnostics/                 (figuras de validación visual)
├── matlab_original/                  ← fuentes MATLAB originales (referencia)
├── docs/                             ← informes HTML y análisis
│   ├── Informe_Depuracion_y_Validacion.html
│   ├── Auditoria_Migracion.html
│   └── MATLAB_VS_PYTHON_ANALYSIS.md
└── generate_migration_audit.py       ← regenera la auditoría HTML
```

## Qué contiene cada archivo

### Código Python (`dengue_model/`)

| Archivo                | Qué hace                                                            |
|------------------------|---------------------------------------------------------------------|
| `config.py`            | Define `ModelConfig` con **todos** los parámetros tunables del modelo. Singleton `CONFIG` mutable. I/O JSON. |
| `my_parameters.py`     | Objeto singleton `P` (fachada). Define `equilibrium_a()` e `initial_state()`. |
| `myODE_ELF.py`         | Sistema de 6 ecuaciones diferenciales + wrapper `solve_model` con diagnósticos. |
| `ELF.py`               | Punto de entrada principal (CLI). Corre la simulación y grafica fracciones. |
| `error_fun_betas.py`   | Función objetivo SSE para calibrar betas contra datos de campo. |
| `diagnostics.py`       | CLI de diagnóstico: barrido de tasas, snapshot de regresión, exportación de figuras. |
| `temp.py`              | Modelo periódico de temperatura anual. |
| `phi_A.py`, `phi_B.py` | Fecundidad base (huevos/hembra/ciclo) por especie. |
| `phi_p_a.py`, `phi_p_b.py` | Tasa de oviposición efectiva per cápita. |
| `psi1_a.py`, `psi1_b.py`   | Tasa de desarrollo huevo → larva. |
| `psi2_a.py`, `psi2_b.py`   | Tasa de desarrollo larva → adulto. |
| `muE_a.py`, `muE_b.py`     | Mortalidad de huevos. |
| `muL_a.py`, `muL_b.py`     | Mortalidad larval. |
| `muF_a.py`, `muF_b.py`     | Mortalidad adulta base (el modelo aplica un multiplicador empírico). |
| `paths.py`             | Rutas centralizadas del paquete. |
| `time_col_date.py`     | Preprocesa CSV de campo → `full_table_Lita.mat`. |
| `params_b_fits.py`     | Recalcula ajustes polinomiales desde CSVs de literatura. |
| `_utils.py`            | `safe_fraction`, `clip_temp_for_poly`, `return_like_input`. |
| `figure_setups.py`     | Configuración común de matplotlib. |

### Suite de validación (`tests/`)

| Archivo                        | Cantidad | Qué valida                                           |
|--------------------------------|----------|------------------------------------------------------|
| `test_baseline.py`             | 13       | Propiedades estructurales: no-NaN, fracciones=1, equilibrio estable, propagación de config. |
| `test_literature_ranges.py`    | 11       | Tasas biológicas dentro de rangos reportados en Yang 2011 / Mordecai 2019. |
| `test_regression.py`           | 1        | Output numérico coincide con snapshot guardado (detecta regresiones). |

### Datos (`data/`)

| Archivo                                      | Qué contiene                                                                |
|----------------------------------------------|-----------------------------------------------------------------------------|
| `full_table_Lita.mat`                        | Datos de ovitrampas de LITA (2018-2021) procesados: fecha, días transcurridos, conteos de aegypti y albopictus. Generado por `time_col_date.py` desde el CSV crudo. |
| `params_literature/*.csv`                    | Valores de literatura usados para ajustar los polinomios de albopictus (`params_b_fits.py`). |
| `python_snapshot.json`                       | **Baseline de regresión**: captura del output del modelo con config por defecto. El test de regresión compara contra este archivo. |
| `diagnostics/rates_vs_temperature.png`       | **Gráfica 1**: las 14 tasas biológicas sobre T ∈ [15, 35] °C. Permite verificar visualmente que cada tasa tiene la forma esperada según la literatura. |
| `diagnostics/rates_vs_temperature.csv`       | Datos tabulados de la gráfica anterior, para inspección manual. |
| `diagnostics/model_fractions.png`            | **Gráfica 2**: dinámica anual del modelo — fracciones de huevos/larvas/adultos para ambas especies a lo largo del año. |

### Documentación (`docs/`)

| Archivo                                    | Qué es                                                              |
|--------------------------------------------|---------------------------------------------------------------------|
| `Informe_Depuracion_y_Validacion.html`     | **Informe principal** del trabajo de depuración y parametrización. Para presentar al equipo. |
| `Auditoria_Migracion.html`                 | Auditoría archivo-por-archivo de la migración MATLAB → Python (diff). |
| `MATLAB_VS_PYTHON_ANALYSIS.md`             | Análisis técnico de diferencias entre los dos lenguajes. |
| `inline_audit_check.js`                    | Script JS usado internamente por la auditoría HTML (inspección cliente). |

### MATLAB original (`matlab_original/`)

Fuentes `.m` originales del modelo Yang Params. Se mantienen como **referencia** para auditar la migración. Si en el futuro se consigue MATLAB, aquí vive `ELF.m` que puede generar el ground-truth numérico.

## Cómo correr el modelo

### Instalación

```bash
pip install numpy scipy matplotlib pandas pytest
```

### Uso básico

```bash
# Simulación con defaults (gráfica emergente)
python -m dengue_model.ELF

# Sin gráficas (modo scripting)
python -m dengue_model.ELF --no-plot

# Cambiar betas por CLI
python -m dengue_model.ELF --beta-ba 0.3 --beta-ab 0.7

# Usar config JSON custom
python -m dengue_model.ELF --config mi_experimento.json
```

### Uso programático

```python
from dengue_model import CONFIG, ModelConfig, run_elf, set_config

# Modificar parámetros
CONFIG.carrying_capacity = 2e5
from dengue_model.my_parameters import rebuild_P; rebuild_P()
result = run_elf(plot=False)

# Cargar config desde archivo
set_config(ModelConfig.from_json("mi_experimento.json"))
```

### Validación

```bash
# Suite completa (debería reportar 25/25 passed)
python -m pytest tests/ -v

# Diagnósticos visuales
python -m dengue_model.diagnostics --plot-rates     # barrido de tasas vs T
python -m dengue_model.diagnostics --compare-snapshot  # regresión contra baseline
```

### Regenerar la auditoría MATLAB ↔ Python

```bash
python generate_migration_audit.py
# Escribe en docs/Auditoria_Migracion.html
```

## Cómo cambiar parámetros

**Todos** los parámetros tunables viven en [`dengue_model/config.py`](dengue_model/config.py) como campos del dataclass `ModelConfig`:

| Bloque                 | Campos                                                                      |
|------------------------|-----------------------------------------------------------------------------|
| Ecosistema             | `carrying_capacity` (K)                                                     |
| Simulación             | `simulation_days`, `num_points`, `albopictus_introduction_day`, `albopictus_intro_eggs` |
| Tasas base             | `bF_aegypti`, `bF_albopictus`, `sigma_aegypti`, `sigma_albopictus`          |
| Ajustes empíricos      | `mortality_adjustment_aegypti` (×3), `mortality_adjustment_albopictus` (×10) |
| Competencia            | `beta_ba`, `beta_ab`                                                        |
| Temperatura            | `temp_baseline_c`, `temp_amplitude`, `temp_shape_k1`, `temp_phase_days`, ...|
| Dominio polinomios     | `poly_temp_min`, `poly_temp_max`                                            |
| Numérica               | `ode_method`, `ode_rtol`, `ode_atol`                                        |

Para generar una plantilla editable:

```bash
python -c "from dengue_model.config import ModelConfig; ModelConfig().save_json('template.json')"
```

Los **coeficientes polinómicos** de las funciones biológicas NO están en config — son constantes físicas derivadas de literatura y viven en cada módulo, documentados en su docstring.

## Cómo interpretar las gráficas

### `data/diagnostics/rates_vs_temperature.png`

Siete paneles mostrando cada una de las 14 tasas biológicas evaluadas sobre T ∈ [15, 35] °C. Azul = *A. aegypti*, rojo = *A. albopictus*. Permite verificar que:

- **Fecundidad base** (phi_A, phi_B): unimodal con pico en rango tropical.
- **Desarrollo larva→adulto** (psi2): monotónico creciente con T saturando.
- **Mortalidades** (muE, muL, muF): forma en U típica (alta en extremos térmicos, mínima en rango óptimo).

Los extremos visuales (T=15 o T=35) pueden verse anómalos por efecto del clipping; esto es esperado y no afecta al modelo porque el modelo de temperatura solo visita ~24–27 °C.

### `data/diagnostics/model_fractions.png`

Dinámica anual del modelo. Seis líneas (tres por especie):

- **Rojo sólido** = fracción de huevos aegypti (Ea frac)
- **Verde punteado** = fracción de larvas aegypti (La frac)
- **Azul punto-raya** = fracción de adultos aegypti (Fa frac)
- **Cian / magenta / amarillo** = equivalentes para albopictus

Interpretación esperada:
- Aegypti: distribución estable a lo largo del año con pequeñas oscilaciones estacionales.
- Albopictus: líneas planas en cero hasta el día 355 (configurable), luego aparición rápida tras la introducción simulada.

## Referencias

- **Yang, H. M. et al.** (2011). Tasas térmicas de *A. aegypti*. *Epidemiology and Infection*.
- **Farnesi, L. C. et al.** (2009). Eclosión y mortalidad de huevos de *A. aegypti*.
- **Mordecai, E. A. et al.** (2019). Thermal biology of mosquito-borne disease.
- **Marini et al.** Desarrollo larval de *A. albopictus*.

## Diferencias frente al MATLAB original

- `solve_ivp (RK45)` reemplaza `ode45`.
- Corrección de bugs: `tspan` indefinido, parámetro `p` no propagado al ODE, validaciones de `ga0` y `isfinite`.
- Parametrización completa vía `ModelConfig` (día 355, multiplicadores, constantes de temperatura).
- Clipping automático de polinomios fuera del rango térmico de ajuste.
- Rutas portables (sin paths hardcodeados a macOS).
