# Yang Params Model — ELF Dengue

Modelo dinámico de competencia entre *Aedes aegypti* y *Aedes albopictus* con 6 compartimentos (huevo / larva / adulto × 2 especies) y tasas biológicas dependientes de temperatura. Migración de MATLAB → Python con corrección de bugs heredados, configuración centralizada y validación.

## Modelo conceptual

Sistema de ecuaciones diferenciales tipo Lotka-Volterra estructurado por etapa. Cada compartimento (E, L, F) evoluciona según tasas de fecundidad `phi_p`, desarrollo `psi1`, `psi2` y mortalidad `mu_E`, `mu_L`, `mu_F`, todas función de la temperatura estacional `T(t)`. La competencia interespecífica actúa sobre el término logístico larval vía los betas `beta_ba` y `beta_ab`.

**Estado `y` (shape 6)**:

| Índice | Variable | Descripción                          |
|--------|----------|--------------------------------------|
| 0      | E_a      | Huevos de A. aegypti                 |
| 1      | L_a      | Larvas de A. aegypti                 |
| 2      | F_a      | Hembras adultas de A. aegypti        |
| 3      | E_b      | Huevos de A. albopictus              |
| 4      | L_b      | Larvas de A. albopictus              |
| 5      | F_b      | Hembras adultas de A. albopictus     |

A. albopictus permanece inactivo hasta el día `config.albopictus_introduction_day` (355 por defecto), simulando la introducción tardía de la especie invasora.

## Cómo correr

```bash
# Simulación con defaults
python -m dengue_model.ELF

# Sin gráficas (útil para scripting)
python -m dengue_model.ELF --no-plot

# Con config JSON custom
python -m dengue_model.ELF --config mi_experimento.json

# Override de betas por CLI
python -m dengue_model.ELF --beta-ba 0.3 --beta-ab 0.7

# Validación contra baseline MATLAB (ver sección de abajo)
python -m dengue_model.ELF --compare-baseline baseline_matlab.json
```

Desde código:

```python
from dengue_model import CONFIG, ModelConfig, run_elf, set_config

# Simulación directa
result = run_elf(plot=False)
print(result["t"].shape, result["y"].shape, result["fractions"].shape)

# Cambiar parámetros antes de correr
CONFIG.beta_ba = 0.3
CONFIG.carrying_capacity = 2e5
from dengue_model.my_parameters import rebuild_P; rebuild_P()
result = run_elf(plot=False)

# O cargar desde JSON
set_config(ModelConfig.from_json("mi_experimento.json"))
```

## Cómo cambiar parámetros

**Todos** los parámetros tunables viven en [`dengue_model/config.py`](dengue_model/config.py) como campos del dataclass `ModelConfig`:

- **Ecosistema**: `carrying_capacity` (K)
- **Simulación**: `simulation_days`, `num_points`, `albopictus_introduction_day`, `albopictus_intro_eggs`
- **Tasas base**: `bF_aegypti`, `bF_albopictus`, `sigma_aegypti`, `sigma_albopictus`
- **Calibración empírica**: `mortality_adjustment_aegypti` (×3), `mortality_adjustment_albopictus` (×10)
- **Competencia**: `beta_ba`, `beta_ab`
- **Temperatura**: `temp_baseline_c`, `temp_amplitude`, `temp_shape_k1`, `temp_phase_days`, ...
- **Dominio polinomios**: `poly_temp_min`, `poly_temp_max`
- **Numérica**: `ode_method`, `ode_rtol`, `ode_atol`

Para generar una plantilla editable:

```bash
python -c "from dengue_model.config import ModelConfig; ModelConfig().save_json('template.json')"
```

Los **coeficientes polinómicos** de las funciones biológicas (`phi_A`, `psi2_a`, `muL_a`, ...) **NO** están en config: son constantes físicas derivadas de literatura (Yang 2011, Farnesi 2009, Mordecai 2019, Marini). Cada módulo documenta su fuente y rango válido en el docstring.

## Mapa de archivos

### Núcleo del modelo

| Archivo                   | Rol                                                                |
|---------------------------|--------------------------------------------------------------------|
| `config.py`               | `ModelConfig` dataclass + `CONFIG` singleton + I/O JSON            |
| `my_parameters.py`        | Objeto `P` (fachada), `equilibrium_a()`, `initial_state()`         |
| `myODE_ELF.py`            | Sistema ODE de 6 compartimentos + wrapper `solve_model`            |
| `ELF.py`                  | Punto de entrada + CLI                                             |
| `error_fun_betas.py`      | Función objetivo SSE para calibrar betas contra datos de campo    |
| `temp.py`                 | Modelo periódico de temperatura anual                              |

### Funciones biológicas (por especie)

|              | A. aegypti        | A. albopictus     | Rol                                |
|--------------|-------------------|-------------------|------------------------------------|
| Fecundidad   | `phi_A.py`        | `phi_B.py`        | huevos·hembra⁻¹·ciclo⁻¹            |
| Oviposición  | `phi_p_a.py`      | `phi_p_b.py`      | huevos·hembra⁻¹·día⁻¹ efectivos   |
| Huevo→larva  | `psi1_a.py`       | `psi1_b.py`       | tasa desarrollo (día⁻¹)            |
| Larva→adulto | `psi2_a.py`       | `psi2_b.py`       | tasa desarrollo (día⁻¹)            |
| Mort. huevo  | `muE_a.py`        | `muE_b.py`        | mortalidad (día⁻¹)                 |
| Mort. larva  | `muL_a.py`        | `muL_b.py`        | mortalidad (día⁻¹)                 |
| Mort. adulto | `muF_a.py`        | `muF_b.py`        | mortalidad base (día⁻¹)            |

### Datos y utilidades

| Archivo                | Rol                                                           |
|------------------------|---------------------------------------------------------------|
| `time_col_date.py`     | Preprocesa CSV de campo → `full_table_Lita.mat`               |
| `params_b_fits.py`     | Recalcula ajustes polinomiales desde CSVs de literatura       |
| `paths.py`             | Rutas centralizadas del paquete                               |
| `_utils.py`            | `safe_fraction`, `clip_temp_for_poly`, `return_like_input`    |
| `figure_setups.py`     | Configuración común de matplotlib                             |

## Validación

Como no disponemos de MATLAB para generar ground truth punto-a-punto, la validación se sostiene en tres pilares complementarios:

### 1. Tests programáticos estructurales (13 tests)

```bash
python -m pytest tests/test_baseline.py -v
```

No-NaN, no-negativos, fracciones suman 1, albopictus latente pre-introducción, equilibrio es punto fijo del ODE, `temp()` en rango biológico, propagación de config.

### 2. Tests de rangos contra literatura (15 tests)

```bash
python -m pytest tests/test_literature_ranges.py -v
```

Valida cada tasa biológica contra valores reportados en Yang 2011 (aegypti), Farnesi 2009 (eclosión) y Mordecai 2019 (albopictus). Chequea picos térmicos, mortalidades adultas dentro de vida esperada (15–60 días), desarrollo larval en rango plausible, unimodalidad de `phi_A`, etc.

### 3. Test de regresión vs snapshot Python

```bash
# Generar snapshot inicial (ya existe en data/python_snapshot.json)
python -m dengue_model.diagnostics --snapshot

# Chequear que ningún cambio rompa la reproducibilidad
python -m pytest tests/test_regression.py -v
# o equivalente:
python -m dengue_model.diagnostics --compare-snapshot
```

Detecta cualquier desviación numérica respecto al output de referencia. Si el cambio es intencional, regenerar el snapshot.

### Diagnósticos visuales

```bash
# Gráfica de las 14 tasas biológicas vs T ∈ [15, 35] °C
python -m dengue_model.diagnostics --plot-rates
# → data/diagnostics/rates_vs_temperature.{png,csv}

# Figura del modelo completo (fracciones por compartimento)
python -m dengue_model.diagnostics --save-figure data/diagnostics/model.png
```

Útil para inspeccionar visualmente que las curvas tengan la forma esperada del paper fuente (unimodal con pico ~27°C para fecundidad, U-shape para mortalidad, etc.).

### Ground-truth MATLAB (pendiente)

Si en el futuro se dispone de MATLAB:

1. En `Yang params model/Yang params model/ELF.m` añadir al final: `save('baseline_matlab.mat', 't', 'y');`
2. Ejecutar `ELF.m` en MATLAB.
3. Convertir a JSON:

    ```python
    from scipy.io import loadmat
    import json, numpy as np
    m = loadmat('baseline_matlab.mat')
    json.dump({'t': np.array(m['t']).ravel().tolist(),
               'y': np.array(m['y']).tolist()}, open('baseline_matlab.json','w'))
    ```

4. Comparar: `python -m dengue_model.ELF --no-plot --compare-baseline baseline_matlab.json`

Tolerancia sugerida: `max_rel_diff < 1%` por compartimento (RK45 Python vs ode45 MATLAB difieren en paso interno).

## Referencias

- **Yang, H. M., et al.** (2011). Coeficientes polinomiales para tasas de *A. aegypti* (muL_a, muF_a, psi2_a, phi_A).
- **Farnesi, L. C., et al.** (2009). Eclosión y mortalidad de huevos de *A. aegypti* vs T (EP, muE_a).
- **Mordecai, E. A., et al.** (2019). Biología térmica de mosquitos vectores — *A. albopictus* (muE_b, muL_b, muF_b, psi2_b).
- **Marini et al.** Desarrollo larval de *A. albopictus* (psi1_b).

## Diferencias frente a MATLAB original

Además de la traducción de lenguaje:

- `solve_ivp (RK45)` reemplaza `ode45`.
- `error_fun_betas.py` corrige bug de `tspan` indefinido.
- `ELF.py`/`myODE_ELF.py` pasan correctamente los betas al ODE (MATLAB no lo hacía).
- Parametrización completa vía `ModelConfig` (día 355, multiplicadores ×3/×10, constantes de temperatura).
- Validaciones: `ga0 > 1` en equilibrium_a, `np.isfinite` en y0, clipping de polinomios fuera del rango térmico de ajuste.
- Rutas portables (adiós `/Users/...` hardcoded).
- `params_b_fits.py` falla explícitamente si faltan CSVs de literatura.

## Auditoría de migración

- Reporte HTML: `Auditoría de Migración Yang Params Model.html`
- Regenerar: `python generate_migration_audit.py`

## Dependencias

```bash
pip install numpy scipy matplotlib pandas pytest
```
