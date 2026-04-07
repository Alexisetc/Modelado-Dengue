__all__ = [
    "DEFAULT_COMPETITION",
    "P",
    "error_fun_betas",
    "initial_state",
    "run_elf",
]


def __getattr__(name):
    if name == "run_elf":
        from .ELF import run_elf

        return run_elf
    if name == "error_fun_betas":
        from .error_fun_betas import error_fun_betas

        return error_fun_betas
    if name in {"DEFAULT_COMPETITION", "P", "initial_state"}:
        from .my_parameters import DEFAULT_COMPETITION, P, initial_state

        exports = {
            "DEFAULT_COMPETITION": DEFAULT_COMPETITION,
            "P": P,
            "initial_state": initial_state,
        }
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
