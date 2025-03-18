import sys
import importlib.util
from pathlib import Path
import mimetypes
import hashlib
import datetime
from typing import Dict, Any, Optional
import json
from dataclasses import dataclass, asdict

@dataclass
class FileMetadata:
    path: str
    size: int
    modified: str
    encoding: str
    suffix: str
    mime_type: str
    hash: str
    is_text: bool
    name: str
    stem: str
    created: float
    symlinks: list[Path] = None
    content: Optional[str] = None

class FilesystemMemory:
    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or Path(__file__).resolve().parent
        self.loaded_modules: Dict[str, Any] = {}
        self.file_metadata: Dict[str, FileMetadata] = {}
        
    def _generate_file_hash(self, file_path: Path) -> str:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _load_text_content(self, path: Path) -> Optional[str]:
        """Load the text content of a file."""
        try:
            return path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return None

    def _extract_file_metadata(self, file_path: Path) -> FileMetadata:
        """Extract metadata from a file."""
        stat = file_path.stat()
        mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        return FileMetadata(
            path=str(file_path),
            size=stat.st_size,
            modified=stat.st_mtime,
            encoding='utf-8',  # Assuming UTF-8 for text files
            suffix=file_path.suffix,
            mime_type=mime_type,
            hash=self._generate_file_hash(file_path),
            is_text='text' in mime_type,
            name=file_path.name,
            stem=file_path.stem,
            created=stat.st_ctime,
            symlinks=[p for p in file_path.parent.glob(f'*{file_path.name}*') if p.is_symlink()],
            content=self._load_text_content(file_path) if 'text' in mime_type else None
        )

    def load_module_from_file(self, file_path: Path) -> Optional[Any]:
        if file_path.suffix != '.py':
            return None
        
        try:
            module_name = f"{file_path.stem}_module"
            spec = importlib.util.spec_from_file_location(module_name, str(file_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"Error loading module from {file_path}: {e}")
            return None
    
    def scan_filesystem(self, ignore_patterns: Optional[list] = None):
        ignore_patterns = ignore_patterns or [
            '.git', '__pycache__', 'venv', '.env', 
            '*.pyc', '*.log', '*.tmp'
        ]
        
        for file_path in self.root_dir.rglob('*'):
            if file_path.is_file():
                if any(file_path.match(pattern) for pattern in ignore_patterns):
                    continue
                
                metadata = self._extract_file_metadata(file_path)
                self.file_metadata[str(file_path)] = metadata
                
                module = self.load_module_from_file(file_path)
                if module:
                    module_name = f"{file_path.stem}_module"
                    self.loaded_modules[module_name] = module
    
    def export_metadata(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        metadata_dict = {
            path: asdict(metadata) 
            for path, metadata in self.file_metadata.items()
        }
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(metadata_dict, f, indent=2)
        
        return metadata_dict

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
        
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        if spec and spec.loader:
            try:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.modules[module_name] = module
            except Exception:
                pass

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

    def create_module(self, metadata: FileMetadata) -> str:
        rel_path = metadata.path.relative_to(self.root_dir)
        module_name = f"content_{rel_path.stem}"
        
        if metadata.mime_type.startswith('text/'):
            content = metadata.path.read_text(errors='replace')
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

def main():
    fs_memory = FilesystemMemory()
    fs_memory.scan_filesystem()
    metadata = fs_memory.export_metadata(
        Path(__file__).parent / 'filesystem_metadata.json'
    )
    
    print(f"Total files scanned: {len(metadata)}")
    print(f"Modules loaded: {len(fs_memory.loaded_modules)}")
    print("File metadata exported to 'filesystem_metadata.json'")
    
    for file_path, meta in list(metadata.items())[:5]:
        print(f"\nFile: {file_path}")
        print(json.dumps(meta, indent=2))

if __name__ == "__main__":
    main()
