from .app import ChildConicityApp

__all__ = ["ChildConicityApp", "run_app"]


def __getattr__(name):
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from .app import ChildConicityApp, run_app

    exports = {
        "ChildConicityApp": ChildConicityApp,
        "run_app": run_app,
    }
    return exports[name]
