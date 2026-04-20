"""Configuración centralizada del modelo ELF (Yang Params) de dengue.

Todos los parámetros tunables del modelo viven aquí. Los coeficientes
polinómicos de las funciones biológicas (phi_*, psi_*, mu_*) son constantes
físicas derivadas de literatura y permanecen en sus respectivos módulos.

Uso básico:
    from dengue_model.config import CONFIG, set_config, ModelConfig

    # Modificar un parámetro puntual:
    CONFIG.carrying_capacity = 2e5
    from dengue_model.my_parameters import rebuild_P; rebuild_P()

    # O cargar desde archivo:
    cfg = ModelConfig.from_json("my_experiment.json")
    set_config(cfg)
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from dataclasses import replace as _dc_replace
from pathlib import Path
from typing import Any


@dataclass
class ModelConfig:
    """Parámetros tunables del modelo ELF.

    Organizado por bloques semánticos. Editar cualquier valor aquí y llamar
    a `set_config()` (o `rebuild_P()` directamente) propaga el cambio al
    objeto singleton `P` en `my_parameters`.
    """

    # === Ecosistema ===
    carrying_capacity: float = 1e5  # K: capacidad de carga larval

    # === Simulación ===
    simulation_days: float = 365.0
    num_points: int = 100
    albopictus_introduction_day: float = 355.0
    albopictus_intro_eggs: float = 10.0  # E_b(t_intro)

    # === Tasas base por especie ===
    bF_aegypti: float = 0.5
    bM_aegypti: float = 0.5
    sigma_aegypti: float = 1.0
    bF_albopictus: float = 0.5
    bM_albopictus: float = 0.5
    sigma_albopictus: float = 1.0

    # === Multiplicadores empíricos de mortalidad adulta ===
    # Origen: MATLAB original (my_parameters.m). Se multiplica muF_a por 3 y
    # muF_b por 10. Razón específica no documentada — tratar como calibración.
    mortality_adjustment_aegypti: float = 3.0
    mortality_adjustment_albopictus: float = 10.0

    # === Competencia interespecífica (betas a calibrar) ===
    beta_ba: float = 0.5  # efecto de albopictus sobre aegypti
    beta_ab: float = 0.5  # efecto de aegypti sobre albopictus

    # === Modelo de temperatura periódica (method=0 de temp.py) ===
    temp_baseline_c: float = 27.04    # so
    temp_offset: float = 0.8949        # c
    temp_amplitude: float = 0.1516     # v
    temp_shape_k1: float = 0.7757      # k1
    temp_phase_days: float = 90.0      # desplazamiento en días
    temp_phase_offset: float = 2.335e-14  # u1 (micro-corrección de fase)

    # === Dominio de validez de polinomios ===
    # Los polinomios de EP (psi1_a) fueron ajustados a datos de Farnesi 2009
    # en el rango [16, 35]°C. Fuera de ese rango, extrapolan a valores
    # inestables. Valores fuera de este rango se clippean y emiten warning.
    poly_temp_min: float = 15.0
    poly_temp_max: float = 35.0

    # === Integración numérica ===
    ode_method: str = "RK45"
    ode_rtol: float = 1e-6
    ode_atol: float = 1e-9

    # === Flags de diagnóstico ===
    warn_on_poly_extrapolation: bool = True
    strict_equilibrium: bool = True  # si False, ga0<=1 no lanza sino que usa la0=0

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------
    def replace(self, **kwargs: Any) -> "ModelConfig":
        """Retorna una copia con campos sobreescritos (no muta self)."""
        return _dc_replace(self, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelConfig":
        known = {f.name for f in fields(cls)}
        unknown = set(data) - known
        if unknown:
            raise ValueError(f"ModelConfig.from_dict: campos desconocidos {unknown}")
        return cls(**{k: v for k, v in data.items() if k in known})

    @classmethod
    def from_json(cls, path: str | Path) -> "ModelConfig":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def save_json(self, path: str | Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


# Singleton global. Mutable intencionalmente.
CONFIG: ModelConfig = ModelConfig()


def set_config(cfg: ModelConfig) -> None:
    """Reemplaza CONFIG global in-place y refresca el objeto P.

    Preserva la identidad del singleton (no reemplaza la referencia), de
    modo que los módulos que hayan hecho `from .config import CONFIG`
    sigan viendo los valores actualizados.
    """
    for field_name in (f.name for f in fields(ModelConfig)):
        setattr(CONFIG, field_name, getattr(cfg, field_name))
    # Propagar a P (import tardío para evitar ciclos)
    from . import my_parameters
    my_parameters.rebuild_P()


def reset_config() -> None:
    """Restaura CONFIG a los valores por defecto."""
    set_config(ModelConfig())
