from __future__ import annotations
import sys
from types import ModuleType, SimpleNamespace
"""This provides a way to dynamically generate modules and inject code into them at runtime. This is useful for creating a
module from a source code string or AST and then executing the module in the runtime. Runtime module (main)
is the module that the source code is injected into."""

def create_module(module_name, module_code, main_module_path):
    """
    Dynamically creates a module with the specified name, injects code into it,
    and adds it to sys.modules.

    Args:
        module_name (str): Name of the module to create.
        module_code (str): Source code to inject into the module.
        main_module_path (str): File path of the main module.

    Returns:
        ModuleType: The dynamically created module.
    """
    # Create a new module
    dynamic_module = ModuleType(module_name)

    # Set attributes for the module
    dynamic_module.__file__ = main_module_path
    dynamic_module.__package__ = module_name
    dynamic_module.__path__ = None
    dynamic_module.__doc__ = None

    # Execute the code and inject it into the module
    exec(module_code, dynamic_module.__dict__)

    # Add the module to sys.modules
    sys.modules[module_name] = dynamic_module

    return dynamic_module

# Example usage:
module_name = "cognos"
module_code = """
def greet():
    print("Hello from demiurge module!")
"""
main_module_path = sys.modules['__main__'].__file__

# Create the dynamic module
dynamic_module = create_module(module_name, module_code, main_module_path)

# Test the dynamic module
dynamic_module.greet()  # Output: Hello from cognos module!

# demonstrate with QuantumMemoryFS object and Future-Participle syntax in triple-double quotes.
