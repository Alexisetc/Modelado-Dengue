# 14. Modelado Dengue

Repositorio del proyecto de modelado poblacional de *Aedes aegypti* y *Aedes albopictus* del INSPI — equipo EpiSIG. Contiene la migración del modelo ELF (Yang Params) desde MATLAB a Python, los datos de campo de la localidad LITA y la literatura de referencia.

## Qué presentar

**El entregable principal es la carpeta [`Yang params model/`](Yang params model/).** Todo lo demás en el repo (datos, literatura) es material de soporte para que el modelo funcione.

Para una lectura rápida empezá por:

1. [`Yang params model/README.md`](Yang params model/README.md) — documentación técnica del modelo.
2. [`Yang params model/docs/Informe_Depuracion_y_Validacion.html`](Yang params model/docs/Informe_Depuracion_y_Validacion.html) — informe visual del trabajo realizado (abrir en navegador).
3. [`Yang params model/docs/Auditoria_Migracion.html`](Yang params model/docs/Auditoria_Migracion.html) — diff detallado MATLAB vs Python archivo por archivo.

## Estructura del repositorio

```
14. Modelado Dengue/
├── README.md                     ← este archivo (visión global)
├── .gitignore
│
├── Yang params model/            ← MODELO (entregable principal)
│   ├── README.md                 ← doc técnica: cómo correr, cómo cambiar parámetros
│   ├── dengue_model/             ← código Python del modelo (paquete)
│   ├── tests/                    ← suite de validación (25 tests)
│   ├── data/                     ← datos procesados, snapshot, figuras
│   ├── matlab_original/          ← fuentes MATLAB originales (referencia)
│   ├── docs/                     ← informes HTML/MD del proyecto
│   └── generate_migration_audit.py  ← regenera la auditoría MATLAB↔Python
│
├── Data Mosquitoes/              ← DATOS DE CAMPO (INSPI, LITA 2018-2021)
│   ├── Raw data/                 ← datos crudos de ovitrampas
│   └── Scripts/                  ← CSV consolidado usado por el modelo
│
└── Literature/                   ← LITERATURA DE REFERENCIA
    ├── Mordecai et al. - 2019 - Thermal biology...pdf
    ├── Mordecai 2017 supplement.pdf
    └── Mosquitoes_Spatial_model.pdf
```

## Qué hace el modelo

Simula la dinámica anual de dos especies competidoras de mosquitos vectores del dengue:

- 6 compartimentos ODE (huevo / larva / adulto × 2 especies)
- Tasas biológicas dependientes de temperatura (Yang 2011, Farnesi 2009, Mordecai 2019)
- Competencia interespecífica en el término logístico larval
- Calibración de los coeficientes de competencia contra datos de campo de LITA

## Cómo correr

```bash
cd "Yang params model"

# Dependencias
pip install numpy scipy matplotlib pandas pytest

# Simulación
python -m dengue_model.ELF

# Validación (25 tests)
python -m pytest tests/ -v

# Diagnósticos (gráficas de tasas vs temperatura)
python -m dengue_model.diagnostics --plot-rates
```

Detalles completos en [`Yang params model/README.md`](Yang params model/README.md).

## Estado del proyecto

- Migración MATLAB → Python: **completada**
- Depuración de bugs heredados: **completada** (7 bugs corregidos)
- Parametrización centralizada: **completada** (`config.py`)
- Suite de validación: **25/25 tests pasan**
- Calibración de betas con datos de LITA: **pendiente** (próxima iteración)
- Validación punto-a-punto contra MATLAB: **pendiente** (requiere instalar MATLAB)

## Contacto

**Responsable:** Alexis Núñez López — EpiSIG INSPI.
