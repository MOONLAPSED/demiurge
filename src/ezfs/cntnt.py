from __future__ import annotations
import weakref
import logging
from collections import defaultdict
from importlib.machinery import SourceFileLoader
from types import ModuleType
"""travels the whole python module tree, triggering inits, and returns
a dictionary of all modules and their inits"""
import mimetypes
import hashlib
from dataclasses import dataclass
from typing import Dict, Optional, Union
from pathlib import Path
import importlib.util
import sys
import json
from datetime import datetime

@dataclass
class FileMetadata:
    path: Path
    mime_type: str
    size: int
    created: float
    modified: float
    hash: str
    symlinks: list[Path] = None
    content: Optional[str] = None

class ModuleLoadError(Exception):
    def __init__(self, module_name: str, path: Path, error: Exception):
        self.module_name = module_name
        self.path = path
        self.error = error
        super().__init__(f"{module_name} ({path}): {error}")

class ContentRegistry:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.metadata: Dict[str, FileMetadata] = {}
        self.modules: Dict[str, weakref.ProxyType] = {}
        self.load_errors: Dict[str, ModuleLoadError] = {}
        self._init_mimetypes()
        self._init_logging()
        self._ignore_patterns = {'.git', '__pycache__', 'venv', 'env', 'node_modules'}
        self.stats = defaultdict(int)  # Change to defaultdict to prevent KeyError
        self.stats.update({
            'files_processed': 0,
            'files_skipped': 0,
            'text_content_loaded': 0,
            'module_load_attempted': 0,
            'module_load_success': 0,
            'module_load_failed': 0,
            'binary_files': 0,
            'total_size': 0
        })
        self.port = 8420

    def _init_mimetypes(self):
        mimetypes.add_type('text/markdown', '.md')
        mimetypes.add_type('text/plain', '.txt')
        mimetypes.add_type('application/python', '.py')

    def _init_logging(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _compute_hash(self, path: Path) -> str:
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _load_text_content(self, path: Path) -> Optional[str]:
        try:
            return path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return None

    def scan_directory(self):
        for path in self.root_dir.rglob('*'):
            if path.is_file() and not any(p in path.parts for p in self._ignore_patterns):
                self.register_file(path)

    def create_module(self, metadata: FileMetadata) -> str:
        """Generate a Python module string representation from file metadata."""
        rel_path = metadata.path.relative_to(self.root_dir)
        module_name = f"content_{rel_path.stem}"
        
        if 'text' in metadata.mime_type:
            content = metadata.content or ''
        else:
            content = f"Binary file: {metadata.mime_type}"
            
        return f'''
"""File: {rel_path}
Type: {metadata.mime_type}
Size: {metadata.size} bytes
Hash: {metadata.hash}
"""

CONTENT = """{content}"""

def get_metadata():
    return {metadata.__dict__}

@lambda _: _()
def init():
    global __file_loaded__
    __file_loaded__ = True
    return True
'''

    def register_file(self, path: Path) -> Optional[FileMetadata]:
        # Update existing method to track binary files and total size
        if not path.is_file() or any(p in path.parts for p in self._ignore_patterns):
            self.stats['files_skipped'] += 1
            return None

        self.stats['files_processed'] += 1
        
        stat = path.stat()
        self.stats['total_size'] += stat.st_size
        mime_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        
        if not 'text' in mime_type:
            self.stats['binary_files'] += 1
        
        content = None
        if 'text' in mime_type:
            content = self._load_text_content(path)
            if content is not None:
                self.stats['text_content_loaded'] += 1
        
        metadata = FileMetadata(
            path=path,
            mime_type=mime_type,
            size=stat.st_size,
            created=stat.st_ctime,
            modified=stat.st_mtime,
            hash=self._compute_hash(path),
            symlinks=[p for p in path.parent.glob(f'*{path.name}*') if p.is_symlink()],
            content=content
        )
        
        if path.suffix == '.py':
            self.stats['module_load_attempted'] += 1
            rel_path = path.relative_to(self.root_dir)
            module_name = f"content_{rel_path.stem}"
            
            try:
                spec = importlib.util.spec_from_file_location(module_name, str(path))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    self.modules[module_name] = weakref.proxy(module)
                    self.stats['module_load_success'] += 1
            except Exception as e:
                self.stats['module_load_failed'] += 1
                self.load_errors[module_name] = ModuleLoadError(module_name, path, e)
                self.logger.warning(f"Module load failed: {module_name} - {str(e)}")

        rel_path = path.relative_to(self.root_dir)
        self.metadata[str(rel_path)] = metadata
        return metadata

    def print_import_summary(self):
        self.logger.info("\nContent Registry Summary")
        self.logger.info("-" * 50)
        self.logger.info(f"Total files processed: {self.stats['files_processed']}")
        self.logger.info(f"Files skipped: {self.stats['files_skipped']}")
        self.logger.info(f"Text content loaded: {self.stats['text_content_loaded']}")
        self.logger.info(f"Binary files: {self.stats['binary_files']}")
        self.logger.info(f"Total size: {self.stats['total_size'] / 1024 / 1024:.2f} MB")
        self.logger.info(f"Python modules:")
        self.logger.info(f"  - Attempted: {self.stats['module_load_attempted']}")
        self.logger.info(f"  - Succeeded: {self.stats['module_load_success']}")
        self.logger.info(f"  - Failed: {self.stats['module_load_failed']}")
        self.logger.info("-" * 50)

    def get_module(self, module_name: str) -> Optional[ModuleType]:
        """Get a loaded module by name."""
        try:
            return self.modules.get(module_name)
        except (weakref.ReferenceError, Exception):
            self.modules.pop(module_name, None)
            return None

    def get_metadata_by_type(self, mime_type: str) -> Dict[str, FileMetadata]:
        """Get all metadata entries for files of a specific MIME type."""
        return {
            k: v for k, v in self.metadata.items() 
            if v.mime_type.startswith(mime_type)
        }

    def export_metadata(self, output_path: Path):
        metadata_dict = {
            str(k): {
                'path': str(v.path),
                'mime_type': v.mime_type,
                'size': v.size,
                'created': datetime.fromtimestamp(v.created).isoformat(),
                'modified': datetime.fromtimestamp(v.modified).isoformat(),
                'hash': v.hash,
                'symlinks': [str(s) for s in (v.symlinks or [])],
                'has_content': v.content is not None,
                'module_status': 'loaded' if k in self.modules else 
                               'failed' if k in self.load_errors else 'not_python'
            }
            for k, v in self.metadata.items()
        }
        
        metadata_dict['__registry_stats__'] = {
            'stats': self.stats,
            'timestamp': datetime.now().isoformat()
        }
        
        output_path.write_text(json.dumps(metadata_dict, indent=2))

    def get_load_errors(self) -> Dict[str, ModuleLoadError]:
        return self.load_errors.copy()

def main():
    registry = ContentRegistry(Path.cwd())
    registry.scan_directory()
    registry.export_metadata(Path('metadata_content.json'))
    registry.print_import_summary()
    return 0

if __name__ == "__main__":
    sys.exit(main())
