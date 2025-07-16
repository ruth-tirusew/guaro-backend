import importlib
import pkgutil
import traceback

def import_routers(package_name):
    print(package_name)
    package = importlib.import_module(package_name)
    prefix = package.__name__ + "."

    for _, module_name, _ in pkgutil.iter_modules(package.__path__, prefix):
        if not module_name.startswith(prefix + "router"):
            continue

        try:
            importlib.import_module(module_name)
        except Exception as e:
            print(traceback.format_exc())
            print(f"Failed to import {module_name}, error: {e}")