import sys
import os
import hashlib
import importlib.util
import json
import inspect
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Set, Any, Optional, Tuple, Callable
import traceback
import re
from functools import partial, wraps


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ModuleIntrospector:
    def __init__(self, hash_algorithm: str = 'sha256'):
        self.hash_algorithm = hash_algorithm

    def _get_hasher(self):
        try:
            return hashlib.new(self.hash_algorithm)
        except ValueError:
            raise ValueError(f"Unsupported hash algorithm: {self.hash_algorithm}")

    def get_file_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Collect comprehensive metadata about a file.
        """
        try:
            stat = os.stat(filepath)
            with open(filepath, 'rb') as f:
                content = f.read()

            hasher = self._get_hasher()
            hasher.update(content)

            return {
                "path": filepath,
                "filename": os.path.basename(filepath),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "hash": hasher.hexdigest(),
                "extension": os.path.splitext(filepath)[1],
            }
        except (FileNotFoundError, PermissionError) as e:
            return {
                "path": filepath,
                "error": str(e)
            }

    def find_file_groups(
        self, 
        base_path: str, 
        max_depth: int = 2, 
        file_filter: Optional[Callable[[str], bool]] = None,
        concurrent_workers: int = 4
    ) -> Dict[str, Set[str]]:
        """
        Group files by their content hash with controlled depth and flexible file filter.
        Uses threading to parallelize I/O bound operations.
        """
        groups: Dict[str, Set[str]] = {}
        file_filter = file_filter or (lambda x: x.endswith(('.py',)))

        def process_file(root, file):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                    hasher = self._get_hasher()
                    hasher.update(content)
                    hash_code = hasher.hexdigest()

                if hash_code not in groups:
                    groups[hash_code] = set()
                groups[hash_code].add(filepath)

            except (PermissionError, IsADirectoryError, OSError) as e:
                logging.warning(f"Could not process file {filepath}: {e}")

        with ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
            for root, _, files in os.walk(base_path):
                depth = root[len(base_path):].count(os.sep)
                if depth > max_depth:
                    continue
                for file in files:
                    if file_filter(file):
                        executor.submit(process_file, root, file)

        return groups

    def inspect_module(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Deeply inspect a Python module by its name instead of path.
        """
        try:
            module = importlib.import_module(module_name)

            module_info = {
                "name": getattr(module, '__name__', 'Unknown'),
                "file": getattr(module, '__file__', 'Unknown path'),
                "doc": getattr(module, '__doc__', 'No documentation'),
                "attributes": {},
                "functions": {},
                "classes": {}
            }

            for name, obj in inspect.getmembers(module):
                if name.startswith('_'):
                    continue

                try:
                    if inspect.isfunction(obj):
                        module_info['functions'][name] = {
                            "signature": str(inspect.signature(obj)),
                            "doc": obj.__doc__
                        }
                    elif inspect.isclass(obj):
                        module_info['classes'][name] = {
                            "methods": [m for m in dir(obj) if not m.startswith('_')],
                            "doc": obj.__doc__
                        }
                    else:
                        module_info['attributes'][name] = str(obj)
                except Exception as member_error:
                    print(f"Error processing member {name}: {member_error}")

            return module_info

        except Exception as e:
            return {
                "error": f"Unexpected error inspecting module: {e}",
                "traceback": traceback.format_exc()
            }


# Utilities for Reverse Polish Notation and Interoperability
def rpn_call(func: Callable, *args):
    """
    Execute a function in Reverse Polish Notation (arguments provided after function).
    """
    @wraps(func)
    def wrapper(*positional_args):
        return func(*reversed(positional_args))
    return wrapper(*args)


# SDK Grammar Helpers
def compose(*funcs):
    """
    Compose multiple functions into one, applying in reverse order.
    """
    def composed_func(arg):
        for func in reversed(funcs):
            arg = func(arg)
        return arg
    return composed_func


def identity(x):
    """
    Identity function for placeholders and introspection utilities.
    """
    return x


def main():
    introspector = ModuleIntrospector(hash_algorithm='sha256')
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print("\n1. Finding File Groups:")
    groups = introspector.find_file_groups(
        project_root,
        max_depth=3,
        file_filter=lambda f: re.match(r'.*\.(py|md|txt)$', f)
    )

    duplicate_groups = {hash_code: files for hash_code, files in groups.items() if len(files) > 1}

    print(f"Total file groups: {len(groups)}")

    if duplicate_groups:
        print("\nDuplicate File Groups:")
        for i, (hash_code, files) in enumerate(duplicate_groups.items(), 1):
            print(f"\nGroup {i} (Hash: {hash_code[:10]}...):")
            for file in files:
                print(f"  - {file}")

            if i >= 10:
                print(f"\n... and {len(duplicate_groups) - 10} more duplicate groups")
                break
    else:
        print("No duplicate files found.")

    print("\n2. Module Inspection Example:")
    try:
        module_details = introspector.inspect_module('json')

        print("\nModule Inspection Results:")
        if 'error' in module_details:
            print("Inspection Error:")
            print(f"  Error: {module_details['error']}")
            if 'traceback' in module_details:
                print("\nDetailed Traceback:")
                print(module_details['traceback'])
        else:
            print(f"Inspected module: {module_details.get('name', 'N/A')}")
            print(f"Module file: {module_details.get('file', 'N/A')}")
            print(f"Functions found: {len(module_details.get('functions', {}))}")
            print(f"Classes found: {len(module_details.get('classes', {}))}")

    except Exception as e:
        print(f"Unexpected error in module inspection: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()