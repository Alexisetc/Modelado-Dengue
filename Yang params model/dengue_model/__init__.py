"""Paquete del modelo ELF (Yang Params) para dinámica poblacional de
A. aegypti y A. albopictus con dependencia térmica.

Entrada típica:
    from dengue_model import run_elf, CONFIG
    CONFIG.beta_ba = 0.3
    result = run_elf()

API pública:
    - run_elf(): correr la simulación (retorna dict con t, y, fractions)
    - error_fun_betas(): función objetivo SSE para calibración de betas
    - CONFIG: singleton mutable de ModelConfig
    - ModelConfig: dataclass con todos los parámetros tunables
    - set_config(cfg): reemplaza CONFIG y refresca P
    - P: singleton de parámetros / referencias de funciones biológicas
    - equilibrium_a(), initial_state(): condiciones iniciales
    - default_competition(): betas actuales [beta_ba, beta_ab]
"""
__all__ = [
    "CONFIG",
    "DEFAULT_COMPETITION",
    "ModelConfig",
    "P",
    "default_competition",
    "equilibrium_a",
    "error_fun_betas",
    "initial_state",
    "run_elf",
    "set_config",
]


def __getattr__(name):
    if name == "run_elf":
        from .ELF import run_elf
        return run_elf
    if name == "error_fun_betas":
        from .error_fun_betas import error_fun_betas
        return error_fun_betas
    if name in {"CONFIG", "ModelConfig", "set_config"}:
        from . import config as _c
        return getattr(_c, name)
    if name in {"DEFAULT_COMPETITION", "P", "default_competition",
                "equilibrium_a", "initial_state"}:
        from . import my_parameters as _p
        return getattr(_p, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
