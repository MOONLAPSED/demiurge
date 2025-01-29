from __future__ import annotations
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

class ContentRegistry:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.metadata: Dict[str, FileMetadata] = {}
        self.modules: Dict[str, Any] = {}
        self._init_mimetypes()

    def _init_mimetypes(self):
        mimetypes.add_type('text/markdown', '.md')
        mimetypes.add_type('text/plain', '.txt')
        mimetypes.add_type('application/python', '.py')

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

    def register_file(self, path: Path) -> Optional[FileMetadata]:
        if not path.is_file():
            return None

        stat = path.stat()
        mime_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        
        metadata = FileMetadata(
            path=path,
            mime_type=mime_type,
            size=stat.st_size,
            created=stat.st_ctime,
            modified=stat.st_mtime,
            hash=self._compute_hash(path),
            symlinks=[p for p in path.parent.glob(f'*{path.name}*') if p.is_symlink()],
            content=self._load_text_content(path) if 'text' in mime_type else None
        )
        
        rel_path = path.relative_to(self.root_dir)
        module_name = f"content_{rel_path.stem}"
        
        # Generate dynamic module
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        if spec and spec.loader:
            try:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.modules[module_name] = module
            except Exception as e:
                print(f"Error loading module from {path}: {e}")
                print(f"Module name: {module_name}")

        self.metadata[str(rel_path)] = metadata
        return metadata

    def scan_directory(self):
        for path in self.root_dir.rglob('*'):
            if path.is_file():
                self.register_file(path)

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
                'has_content': v.content is not None
            }
            for k, v in self.metadata.items()
        }
        output_path.write_text(json.dumps(metadata_dict, indent=2))

def main():
    registry = ContentRegistry(Path.cwd())
    registry.scan_directory()
    registry.export_metadata(Path('metadata_content.json'))
    return 0

if __name__ == "__main__":
    sys.exit(main())
