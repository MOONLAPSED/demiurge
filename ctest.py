from __future__ import annotations
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Standard Library Imports - 3.13 std libs **ONLY**
#------------------------------------------------------------------------------
import os
import io
import re
import sys
import ast
import dis
import mmap
import json
import uuid
import site
import time
import cmath
import errno
import shlex
import ctypes
import signal
import random
import pickle
import socket
import struct
import pstats
import shutil
import tomllib
import decimal
import pathlib
import logging
import inspect
import asyncio
import hashlib
import argparse
import cProfile
import platform
import tempfile
import mimetypes
import functools
import linecache
import traceback
import threading
import importlib
import subprocess
import tracemalloc
import http.server
from math import sqrt
from io import StringIO
from array import array
from queue import Queue, Empty
from abc import ABC, abstractmethod
from enum import Enum, auto, StrEnum
from collections import namedtuple
from operator import mul
from typing import (
    Any, Dict, List, Optional, Union, Callable, TypeVar,
    Tuple, Generic, Set, Coroutine, Type, NamedTuple,
    ClassVar, Protocol, runtime_checkable, AsyncIterator
)
from types import (
    SimpleNamespace, ModuleType, MethodType,
    FunctionType, CodeType, TracebackType, FrameType
)
from dataclasses import dataclass, field
from functools import reduce, lru_cache, partial, wraps
from collections.abc import Iterable, Mapping
from datetime import datetime
from pathlib import Path, PureWindowsPath
from contextlib import contextmanager, asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from functools import reduce
from importlib.util import spec_from_file_location, module_from_spec
libc = None
IS_WINDOWS = os.name == 'nt'
IS_POSIX = os.name == 'posix'
if IS_WINDOWS:
    try:
        from ctypes import windll
        from ctypes import wintypes
        from ctypes.wintypes import HANDLE, DWORD, LPWSTR, LPVOID, BOOL
        from pathlib import PureWindowsPath
        def set_process_priority(priority: int):
            windll.kernel32.SetPriorityClass(wintypes.HANDLE(-1), priority)
        libc = ctypes.windll.msvcrt
        set_process_priority(1)
    except ImportError:
        print(f"{__file__} failed to import ctypes on platform: {os.name}")
elif IS_POSIX:
    try:
        libc = ctypes.CDLL("libc.so.6")
    except ImportError:
        print(f"{__file__} failed to import ctypes on platform: {os.name}")
"""
Top-level monolithic application logic:
- File content registration and metadata storage.
- Dynamic discovery and loading of modules.
- Platform-aware FFI calls.
- ASGI-compatible HTTP app.
- Native IPv6 datagram handling.
"""
@dataclass
class MimeTypeData:
    """The MIME types which this application handles (whitelist)."""
    def _init_mimetypes(self):
        mimetypes.add_type('text/markdown', '.md')
        mimetypes.add_type('text/plain', '.txt')
        # mimetypes.add_type('application/python', '.py')

@dataclass
class FilterData:
    """Contains data and logic for filtering files."""
    file_filters: Set[str] = field(default_factory=set)
    directory_filters: Set[str] = field(default_factory=set)

    def _init_filters(self):
        # Initialize file filters (e.g., extensions to exclude)
        self.file_filters.update({'.tmp', '.log', '.bak'})

        # Initialize directory filters (e.g., directories to exclude)
        self.directory_filters.update({'__pycache__', '.git', '.svn'})

    def should_exclude_file(self, path: Path) -> bool:
        """Determine if a file should be excluded based on its extension."""
        return path.suffix in self.file_filters

    def should_exclude_directory(self, path: Path) -> bool:
        """Determine if a directory should be excluded based on its name."""
        return path.name in self.directory_filters

def scan_directory(root_dir: Path, filters: FilterData):
    """Scan directory applying filters."""
    for path in root_dir.rglob('*'):
        if path.is_dir():
            if filters.should_exclude_directory(path):
                continue
        elif path.is_file():
            if filters.should_exclude_file(path):
                continue

        # Process the file or directory
        print(f"Processing {path}")

# Example usage
filters = FilterData()
filters._init_filters()
scan_directory(Path(__file__), filters)

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
        # mimetypes.add_type('application/python', '.py') 
        # # Not-needed if we use the Python interpreter to run the app.

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

# Example ASGI app
async def app(scope, receive, send):
    if scope['type'] == 'http':
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [(b'content-type', b'text/plain')]
        })
        await send({
            'type': 'http.response.body',
            'body': b'Hello, ASGI world!'
        })

# Native IPv6 Datagram Handler
async def ipv6_echo_server():
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    sock.bind(('::1', 9999))
    print("Listening for IPv6 datagrams on port 9999...")

    while True:
        data, addr = sock.recvfrom(1024)
        print(f"Received {data} from {addr}")
        sock.sendto(data, addr)

# Shell Command Execution
def execute_command(command: str):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

# Main entry point
async def main():
    registry = ContentRegistry(Path.cwd())
    registry.scan_directory()
    registry.export_metadata(Path('metadata_content.json'))

    # FFI Call Example
    libc.printf(b"Hello from C library\n")

    # Execute shell command
    if IS_POSIX:
        print("POSIX Shell Output:", execute_command("echo 'Hello from shell'"))
    elif IS_WINDOWS:
        print("Windows Shell Output:", execute_command("echo Hello from shell"))

    # Start IPv6 Echo Server
    asyncio.create_task(ipv6_echo_server())

    # Run ASGI App Example
    print("Starting ASGI app...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Application interrupted.")
