import sys
import os
import hashlib
import importlib.util
import logging
import inspect
from types import ModuleType
from typing import Dict, Set, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ModularSystem:
    def __init__(self, hash_algorithm: str = 'sha256'):
        self.hash_algorithm = hash_algorithm
        self.modules: Dict[str, ModuleType] = {}

    def _get_hasher(self):
        try:
            return hashlib.new(self.hash_algorithm)
        except ValueError:
            raise ValueError(f"Unsupported hash algorithm: {self.hash_algorithm}")

    def get_file_metadata(self, filepath: str) -> Dict[str, Any]:
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
            logging.error(f"Error accessing file {filepath}: {e}")
            return {"path": filepath, "error": str(e)}

    def find_file_groups(self, base_path: str, max_depth: int = 2, file_filter: Optional[Callable[[str], bool]] = None) -> Dict[str, Set[str]]:
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

        with ThreadPoolExecutor(max_workers=4) as executor:
            for root, _, files in os.walk(base_path):
                depth = root[len(base_path):].count(os.sep)
                if depth > max_depth:
                    continue
                for file in files:
                    if file_filter(file):
                        executor.submit(process_file, root, file)

        return groups

    def inspect_module(self, module_name: str) -> Optional[Dict[str, Any]]:
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
                    logging.warning(f"Error processing member {name}: {member_error}")
            return module_info
        except Exception as e:
            logging.error(f"Error inspecting module {module_name}: {e}")
            return {"error": str(e)}

    def create_module(self, module_name: str, module_code: str, **kwargs) -> Optional[ModuleType]:
        try:
            dynamic_module = ModuleType(module_name)
            dynamic_module.__dict__.update(kwargs)
            exec(module_code, dynamic_module.__dict__)
            sys.modules[module_name] = dynamic_module
            self.modules[module_name] = dynamic_module
            logging.info(f"Dynamic module '{module_name}' created successfully.")
            return dynamic_module
        except Exception as e:
            logging.error(f"Failed to create dynamic module '{module_name}': {e}")
            return None

    def main(self, base_path: str, depth: int = 2):
        logging.info("\n1. Finding File Groups:")
        file_groups = self.find_file_groups(base_path, max_depth=depth)
        duplicate_groups = {hash_code: files for hash_code, files in file_groups.items() if len(files) > 1}
        logging.info(f"Total file groups: {len(file_groups)}")

        if duplicate_groups:
            logging.info("\nDuplicate File Groups:")
            for i, (hash_code, files) in enumerate(duplicate_groups.items(), 1):
                logging.info(f"\nGroup {i} (Hash: {hash_code[:10]}...):")
                for file in files:
                    logging.info(f"  - {file}")
                if i >= 10:
                    logging.info(f"\n... and {len(duplicate_groups) - 10} more duplicate groups")
                    break

        logging.info("\n2. Module Inspection Example:")
        module_name = 'json'
        module_details = self.inspect_module(module_name)
        if module_details and 'error' in module_details:
            logging.error(f"Inspection Error: {module_details['error']}")
        else:
            logging.info(f"Inspected module: {module_details['name']}")
            logging.info(f"Module file: {module_details['file']}")
            logging.info(f"Functions found: {len(module_details.get('functions', {}))}")
            logging.info(f"Classes found: {len(module_details.get('classes', {}))}")

if __name__ == "__main__":
    system = ModularSystem(hash_algorithm='sha256')
    project_root = os.path.abspath('.')
    system.main(base_path=project_root, depth=3)