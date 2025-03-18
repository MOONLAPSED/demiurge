#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations
#------------------------------------------------------------------------------
# Standard Library Imports - 3.13 std libs **ONLY**
#------------------------------------------------------------------------------
import re
import gc
import os
import dis
import sys
import ast
import time
import site
import mmap
import json
import uuid
import math
import cmath
import shlex
import socket
import struct
import shutil
import pickle
import ctypes
import pstats
import weakref
import logging
import tomllib
import pathlib
import asyncio
import inspect
import hashlib
import cProfile
import argparse
import tempfile
import platform
import traceback
import functools
import linecache
import importlib
import threading
import subprocess
import tracemalloc
import http.server
import collections
import http.client
import http.server
import socketserver
from array import array
from io import StringIO
from pathlib import Path
from math import sqrt, pi
from datetime import datetime
from queue import Queue, Empty
from abc import ABC, abstractmethod, ABCMeta
from dataclasses import dataclass, field
from importlib.machinery import ModuleSpec
from collections.abc import Iterable, Mapping
from concurrent.futures import ThreadPoolExecutor
from enum import Enum, auto, IntEnum, StrEnum, Flag
from collections import defaultdict, deque, namedtuple
from functools import reduce, lru_cache, partial, wraps
from contextlib import contextmanager, asynccontextmanager
from importlib.util import spec_from_file_location, module_from_spec
from types import SimpleNamespace, ModuleType,  MethodType, FunctionType, CodeType, TracebackType, FrameType
from typing import (
    Any, Dict, List, Optional, Union, Callable, TypeVar, Tuple, Generic, Set, OrderedDict,
    Coroutine, Type, NamedTuple, ClassVar, Protocol, runtime_checkable, AsyncIterator, Iterator
)
IS_WINDOWS = os.name == 'nt'
IS_POSIX = os.name == 'posix'
profiler = cProfile.Profile()
if IS_WINDOWS:
    from ctypes import windll
    from ctypes import wintypes
    from ctypes.wintypes import HANDLE, DWORD, LPWSTR, LPVOID, BOOL
    from pathlib import PureWindowsPath
    def set_process_priority(priority: int):
        windll.kernel32.SetPriorityClass(wintypes.HANDLE(-1), priority)
    if __name__ == '__main__':
        set_process_priority(1)
elif IS_POSIX:
    import resource
    def set_process_priority(priority: int):
        try:
            os.nice(priority)
        except PermissionError:
            print("Warning: Unable to set process priority. Running with default priority.")
    if __name__ == '__main__':
        set_process_priority(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_port_available(port: int) -> bool:
    """Check if a given port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('127.0.0.1', port))
        return result != 0  # If the result is not 0, the port is available

def find_available_port(start_port: int) -> int:
    """Find an available port starting from start_port."""
    port = start_port
    while not is_port_available(port):
        logger.info(f"Port {port} is occupied. Trying next port.")
        port += 1
    logger.info(f"Found available port: {port}")
    return port

@lambda _: _()
def FireFirst() -> None:
    """Function that fires on import."""
    # profiler.enable()
    # logger.info("Profiler enabled.")
    PORT = 8420
    try:
        available_port = find_available_port(PORT)
        logger.info(f"Using port: {available_port}")
        print(f'func you')
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        return True  # Fires as soon as Python sees it

"""Core Operators:

Composition (@): Sequential application of operations
Tensor Product (*): Parallel combination of operations
Direct Sum (+): Alternative pathways of computation
Adjoint (†): Reversal/dual of operations


Fundamental Structures:

Particle: Quantum of computation
ComputationalOperator: Base class for all operators
DensityMatrix: Statistical state of the system
ComputationalField: Space where computation occurs


Algebraic Properties:

Associativity: (A @ B) @ C = A @ (B @ C)
Distributivity: A * (B + C) = (A * B) + (A * C)
Adjoint rules: (A @ B)† = B† @ A†"""

T = TypeVar('T')  # Type structure (static/potential)
V = TypeVar('V')  # Value space (measured/actual)
C = TypeVar('C')  # Computation space (transformative)

class QuantumState(Enum):
    SUPERPOSITION = "SUPERPOSITION"  # Handle-only, like PyObject*
    ENTANGLED = "ENTANGLED"         # Referenced but not fully materialized
    COLLAPSED = "COLLAPSED"         # Fully materialized Python object
    DECOHERENT = "DECOHERENT"      # Garbage collected
class OperatorType(Enum):
    """Fundamental types of operations in our computational universe"""
    COMPOSITION = auto()   # Function composition (>>)
    TENSOR = auto()       # Tensor product (⊗)
    DIRECT_SUM = auto()   # Direct sum (⊕)
    OUTER = auto()        # Outer product (|ψ⟩⟨φ|)
    ADJOINT = auto()      # Hermitian adjoint (†)
    MEASUREMENT = auto()  # Quantum measurement (⟨M|ψ⟩)

@dataclass(frozen=True)
class ModuleMetadata:
    """Metadata for lazy module loading."""
    original_path: Path
    module_name: str
    is_python: bool
    file_size: int
    mtime: float
    content_hash: str  # For change detection

@dataclass
class Particle(Generic[T, V, C]):
    """
    The fundamental unit of our computational universe.
    Analogous to a quantum particle with state, operators, and measurement.
    """
    state_vector: complex
    phase: float
    type_structure: T
    value_space: V
    compute_space: C
    probability_amplitude: complex = field(default_factory=lambda: complex(1.0, 0.0))
    
    def __matmul__(self, other: Particle) -> Particle:
        """Tensor product operator (⊗)"""
        return Particle(
            state_vector=self.state_vector * other.state_vector,
            phase=(self.phase + other.phase) % (2 * pi),
            type_structure=(self.type_structure, other.type_structure),
            value_space=(self.value_space, other.value_space),
            compute_space=lambda x: self.compute_space(other.compute_space(x))
        )
    
    def compose(self, other: Particle) -> Particle:
        """Function composition operator (>>)"""
        return Particle(
            state_vector=self.state_vector * other.state_vector,
            phase=self.phase,
            type_structure=other.type_structure,
            value_space=other.value_space,
            compute_space=lambda x: other.compute_space(self.compute_space(x))
            )

class PyObjectBridge:
    """
    Direct bridge to CPython's object implementation.
    Provides raw access to the fundamental C structure of Python objects.
    """
    class CPyObject(ctypes.Structure):
        """Mirror of PyObject C structure"""
        _fields_ = [
            ("ob_refcnt", ctypes.c_ssize_t),
            ("ob_type", ctypes.c_void_p)
        ]

    @staticmethod
    def get_refcount(obj: Any) -> int:
        """Get raw reference count from PyObject"""
        return ctypes.cast(id(obj), ctypes.POINTER(PyObjectBridge.CPyObject)).contents.ob_refcnt
@dataclass
class StateVector:
    """Represents a quantum state vector with amplitude and phase."""
    amplitude: complex
    phase: float
    data: Any
    timestamp: float
    
    def interfere(self, other: "StateVector") -> "StateVector":
        """Perform quantum interference with another state vector."""
        new_amplitude = self.amplitude * other.amplitude
        new_phase = (self.phase + other.phase) % (2 * math.pi)
        return StateVector(new_amplitude, new_phase, self.data)


class Frame(Generic[T, V, C], metaclass=ABCMeta):
    """
    A fundamental frame of reference that bridges between:
    1. CPython's concrete object model
    2. Our abstract quantum information space
    3. The runtime's type system
    
    This is the 'godparent' structure that provides the fundamental interface
    between all three aspects of our system.

    A Frame is the quantum bridge between CPython's memory model and our associative space.
    It represents a region of memory that can exist in multiple states and maintains
    quantum-like properties while mapping directly to CPython's object system.
    """
    def __init__(self):
        self._handle = id(self)  # Raw CPython object handle
        self._state = QuantumState.SUPERPOSITION
        self._type_structure: Optional[T] = None
        self._value_space: Optional[V] = None
        self._compute_space: Optional[C] = None
        self._references: weakref.WeakSet = weakref.WeakSet()
    def __init__(self):
        # Map to CPython's object structure
        self._py_object = ctypes.py_object()
        self._ref_count = ctypes.c_ssize_t()
        self._type_ptr = ctypes.c_void_p()
        
        # Quantum state management
        self._state = QuantumState.SUPERPOSITION
        self._observers: set[weakref.ref] = set()
        
        # Type-Value-Computation spaces
        self._type_space: Optional[T] = None
        self._value_space: Optional[V] = None
        self._compute_space: Optional[C] = None

    @property
    def state(self) -> QuantumState:
        return self._state
        
    def collapse(self) -> V:
        """Forces materialization of the value space."""
        if self._state == QuantumState.SUPERPOSITION:
            self._materialize()
        return self._value_space

    def _materialize(self) -> None:
        """Maps the quantum state to actual CPython objects."""
        if self._value_space is not None:
            self._py_object.value = self._value_space
            # Get actual CPython object internals
            obj_ptr = ctypes.cast(id(self._py_object.value), ctypes.c_void_p)
            # Map to PyObject structure
            self._ref_count.value = ctypes.pythonapi.Py_RefCnt(obj_ptr)
            self._type_ptr.value = ctypes.pythonapi.Py_TYPE(obj_ptr)
            self._state = QuantumState.COLLAPSED

    @property
    def handle(self) -> int:
        """Raw CPython object handle (like PyObject*)"""
        return self._handle
        
    @property
    def refcount(self) -> int:
        """Direct access to CPython's reference count"""
        return PyObjectBridge.get_refcount(self)
    
    def materialize(self) -> None:
        """
        Forces materialization of the frame, transitioning from
        handle-only to full Python object with type structure.
        """
        if self._state == QuantumState.SUPERPOSITION:
            # Materialize type structure first
            self._type_structure = self._materialize_type()
            self._state = QuantumState.ENTANGLED
            
    def collapse(self) -> V:
        """
        Fully collapses the frame into a concrete value,
        materializing all aspects (type, value, compute).
        """
        if self._state != QuantumState.COLLAPSED:
            self.materialize()  # Ensure type structure exists
            self._value_space = self._collapse_value()
            self._compute_space = self._create_compute_space()
            self._state = QuantumState.COLLAPSED
        return self._value_space

    @abstractmethod
    def _materialize_type(self) -> T:
        """Create the type structure for this frame"""
        pass
        
    @abstractmethod
    def _collapse_value(self) -> V:
        """Collapse into concrete value"""
        pass
        
    @abstractmethod
    def _create_compute_space(self) -> C:
        """Create computation space for operations"""
        pass


class ObjectFrame(Frame[type, Any, callable]):
    """Concrete frame implementation for regular Python objects"""
    
    def _materialize_type(self) -> type:
        """Map to Python's type system"""
        if self._initial is not None:
            return type(self._initial)
        return object

class DegreeOfFreedom(Frame[T, V, C], ABC):
    """
    Represents a single degree of freedom in our quantum information space.
    Maps directly to a PyObject while maintaining quantum state semantics.
    """
    def __init__(self, initial_state: Optional[Union[T, V, C]] = None):
        super().__init__()
        self._initial = initial_state
        
    def __del__(self):
        """Handle decoherence when garbage collected"""
        self._state = QuantumState.DECOHERENT
        
    def entangle(self, other: DegreeOfFreedom) -> None:
        """Create quantum entanglement between degrees of freedom"""
        if self._state == QuantumState.SUPERPOSITION:
            self.materialize()
        self._references.add(other)
        self._state = QuantumState.ENTANGLED

class Field(Frame[T, V, C], ABC):
    """
    An information field that contains and manages multiple degrees of freedom.
    Provides the space in which quantum information dynamics occur.
    It extends Frame with composition and transformation capabilities.
    """
    def __init__(self):
        super().__init__()
        self._degrees: weakref.WeakSet[DegreeOfFreedom] = weakref.WeakSet()
        self.entangled_fields: set[weakref.ref[Field]] = set()
        
    def entangle(self, other: Field) -> None:
        """Creates quantum entanglement between fields."""
        self.entangled_fields.add(weakref.ref(other))
        other.entangled_fields.add(weakref.ref(self))
        self._state = QuantumState.ENTANGLED
        other._state = QuantumState.ENTANGLED
        
    @abstractmethod
    def transform(self, operator: Callable[[V], V]) -> None:
        """Applies a transformation operator to the value space."""
        pass

    def create_degree(self, initial_state: Optional[Union[T, V, C]] = None) -> DegreeOfFreedom[T, V, C]:
        """Create new degree of freedom in this field"""
        degree = DegreeOfFreedom(initial_state)
        self._degrees.add(degree)
        return degree
        
    def collapse_all(self) -> None:
        """Collapse all degrees of freedom in the field"""
        for degree in self._degrees:
            degree.collapse()
        
class Space(Field[T, V, C], ABC):
    """
    Space is the container for Fields and manages their interactions.
    It provides the high-level interface for our quantum memory model.
    """
    def __init__(self):
        super().__init__()
        self.fields: dict[str, Field] = {}
        
    def create_field(self, handle: str) -> Field:
        """Creates a new field in this space."""
        field = Field()
        self.fields[handle] = field
        return field
        
    def compose(self, other: Space) -> Space:
        """Composes two spaces, maintaining quantum properties."""
        new_space = Space()
        # Compose fields while preserving quantum states
        for handle, field in self.fields.items():
            if handle in other.fields:
                new_field = new_space.create_field(handle)
                new_field.entangle(field)
                new_field.entangle(other.fields[handle])
        return new_space
    
    def _collapse_value(self) -> Any:
        """Create concrete Python object"""
        if self._initial is not None:
            return self._initial
        return None
        
    def _create_compute_space(self) -> callable:
        """Map to Python's method/callable space"""
        return lambda x: x  # Identity function as default

@dataclass
class MorphologicalRule(ABC, ABCMeta):
    """
    Rules that map structural transformations in code morphologies.
    """
    symmetry: str  # e.g., "Translation", "Rotation", "Phase"
    conservation: str  # e.g., "Information", "Coherence", "Behavioral"
    lhs: str  # Left-hand side element (morphological pattern)
    rhs: List[Union[str, 'MorphologicalRule']]  # Right-hand side after transformation

    def apply(self, input_seq: List[str]) -> List[str]:
        """
        Applies the morphological transformation to an input sequence.
        """
        if self.lhs in input_seq:
            idx = input_seq.index(self.lhs)
            return input_seq[:idx] + [elem for elem in self.rhs] + input_seq[idx + 1:]
        return input_seq

# need help from here-onwards
class ModuleIndex:
    """Maintains an index of modules with metadata, supporting lazy loading."""
    def __init__(self, max_cache_size: int = 1000):
        self.index: Dict[str, ModuleMetadata] = {}
        self.cache = OrderedDict()  # LRU cache for loaded modules
        self.max_cache_size = max_cache_size
        self.lock = threading.RLock()

    def add(self, module_name: str, metadata: ModuleMetadata) -> None:
        with self.lock:
            self.index[module_name] = metadata

    def get(self, module_name: str) -> Optional[ModuleMetadata]:
        with self.lock:
            return self.index.get(module_name)

    def cache_module(self, module_name: str, module: Any) -> None:
        with self.lock:
            if len(self.cache) >= self.max_cache_size:
                _, oldest_module = self.cache.popitem(last=False)
                if oldest_module.__name__ in sys.modules:
                    del sys.modules[oldest_module.__name__]
            self.cache[module_name] = module

    def _profile_module(self, metadata: ModuleMetadata):
        """Automatically profile the module content."""
        profiler = cProfile.Profile()
        profiler.enable()
        self.load_module_content(metadata.module_name)
        profiler.disable()
        self._print_profile_data(metadata.module_name)

    def _print_profile_data(self, module_name):
        s = StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(self.profiler, stream=s).sort_stats(sortby)
        ps.print_stats()
        profile_data = s.getvalue()
        logging.info(f"Profile data for {module_name}: \n{profile_data}")

class QuantumModuleLoader:
    """
    Creates modules that exist in superposition until observed through import.
    Uses importlib machinery but maintains quantum state awareness.
    """
    def __init__(self):
        self._module_cache: Dict[str, Any] = {}
        self._state_registry: Dict[str, QuantumState] = {}
        
    def create_module(self, name: str, path: Path) -> Optional[Any]:
        # Create the module spec (quantum superposition)
        spec = spec_from_file_location(name, path)
        if spec is None:
            return None
            
        # Module exists in superposition until we materialize it
        self._state_registry[name] = QuantumState.SUPERPOSITION
        
        # Create but don't execute module (maintain superposition)
        module = module_from_spec(spec)
        
        # Inject our quantum-aware loader
        def quantum_exec_module(m):
            # State collapses when module code executes
            self._state_registry[name] = QuantumState.ENTANGLED
            spec.loader.exec_module(m)  # type: ignore
            self._state_registry[name] = QuantumState.COLLAPSED
            
        # Replace standard loader with our quantum-aware version
        if spec.loader:
            spec.loader.exec_module = quantum_exec_module  # type: ignore
            
        return module

    def get_module_state(self, name: str) -> QuantumState:
        return self._state_registry.get(name, QuantumState.DECOHERENT)

class ScalableReflectiveRuntime:
    """A scalable runtime system managing lazy loading, caching, and module generation."""
    def __init__(self, base_dir: Path, max_cache_size: int = 1000, max_workers: int = 4, chunk_size: int = 1024 * 1024):
        self.base_dir = Path(base_dir)
        self.module_index = ModuleIndex(max_cache_size)
        self.excluded_dirs = {'.git', '__pycache__', 'venv', '.env'}
        self.module_cache_dir = self.base_dir / '.module_cache'
        self.chunk_size = chunk_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.index_path = self.module_cache_dir / 'module_index.pkl'

    def _load_content(self, path: Path, use_mmap: bool = True) -> str:
        """Load file content efficiently."""
        if not use_mmap or path.stat().st_size < self.chunk_size:
            return path.read_text(encoding='utf-8', errors='replace')
        with open(path, 'r+b') as f:
            mm = mmap.mmap(f.fileno(), 0)
            try:
                return mm.read().decode('utf-8', errors='replace')
            finally:
                mm.close()

    def scan_directory(self) -> None:
        """Scan directory to build the module index."""
        for chunk in self._scan_directory_chunks():
            self._process_file_chunk(chunk)

    def save_index(self) -> None:
        """Persist the module index to disk."""
        self.module_cache_dir.mkdir(exist_ok=True)
        with open(self.index_path, 'wb') as f:
            pickle.dump(self.module_index.index, f)

    def load_index(self) -> bool:
        """Load a previously saved module index."""
        try:
            if self.index_path.exists():
                with open(self.index_path, 'rb') as f:
                    self.module_index.index = pickle.load(f)
                return True
        except Exception as e:
            logging.error(f"Error loading index: {e}")
        return False

    def _compute_file_hash(self, path: Path) -> str:
        """Compute a hash for the file content."""
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(self.chunk_size), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _scan_directory_chunks(self) -> Iterator[Set[Path]]:
        current_chunk = set()
        chunk_size = 1000  # files per chunk

        for path in self.base_dir.rglob('*'):
            if path.is_file() and not any(p.name in self.excluded_dirs for p in path.parents):
                current_chunk.add(path)
                if len(current_chunk) >= chunk_size:
                    yield current_chunk
                    current_chunk = set()

        if current_chunk:
            yield current_chunk

    def _process_file_chunk(self, paths: Set[Path]) -> None:
        def process_single_file(path: Path) -> Optional[ModuleMetadata]:
            try:
                stat = path.stat()
                metadata = ModuleMetadata(
                    original_path=path,
                    module_name=self._sanitize_module_name(path),
                    is_python=path.suffix == '.py',
                    file_size=stat.st_size,
                    mtime=stat.st_mtime,
                    content_hash=self._compute_file_hash(path)
                )
                return metadata
            except Exception as e:
                logging.error(f"Error processing {path}: {e}")
                return None

        futures = [self.executor.submit(process_single_file, path) for path in paths]
        for future in futures:
            try:
                metadata = future.result()
                if metadata:
                    self.module_index.add(metadata.module_name, metadata)
            except Exception as e:
                logging.error(f"Error processing file chunk: {e}")



@dataclass
class EmbeddingConfig:
    dimensions: int = 768
    precision: str = 'float32'
    encoding: str = 'utf8'
    cluster_count: int = 8
    cache_path: str = 'runtime_cache.json'
    
    def get_format_char(self) -> str:
        return {'float32': 'f', 'float64': 'd', 'int32': 'i'}[self.precision]

@dataclass
class Document:
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict = None
    uuid: str = None

    def __post_init__(self):
        if self.uuid is None:
            self.uuid = str(uuid.uuid4())

class MerkleNode:
    def __init__(self, data: Any, children: Set['MerkleNode'] = None):
        self.data = data
        self.children = children or set()
        self.timestamp = datetime.utcnow().isoformat()
        self.uuid = str(uuid.uuid4())
        self.hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        hasher = hashlib.sha256()
        hasher.update(str(self.data).encode())
        for child in sorted(self.children, key=lambda x: x.hash):
            hasher.update(child.hash.encode())
        return hasher.hexdigest()

    def add_child(self, child: 'MerkleNode'):
        self.children.add(child)
        self.hash = self._calculate_hash()

class RuntimeState:
    def __init__(self):
        self.merkle_root: Optional[MerkleNode] = None
        self.object_map: Dict[str, MerkleNode] = {}
        self.state_history: List[str] = []

class OllamaClient:
    def __init__(self, host: str = "localhost", port: int = 11434):
        self.host = host
        self.port = port

    async def generate_embedding(self, text: str, model: str = "nomic-embed-text") -> Optional[List[float]]:
        try:
            conn = http.client.HTTPConnection(self.host, self.port)
            request_data = {
                "model": model,
                "prompt": text
            }
            headers = {'Content-Type': 'application/json'}
            
            conn.request("POST", "/api/embeddings", json.dumps(request_data), headers)
            response = conn.getresponse()
            result = json.loads(response.read().decode())
            return result['embedding']
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return None
        finally:
            conn.close()

    async def generate_response(self, prompt: str, model: str = "gemma:2b") -> str:
        try:
            conn = http.client.HTTPConnection(self.host, self.port)
            request_data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            headers = {'Content-Type': 'application/json'}
            
            conn.request("POST", "/api/generate", json.dumps(request_data), headers)
            response = conn.getresponse()
            result = json.loads(response.read().decode())
            return result.get('response', '')
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return f"Error generating response: {str(e)}"
        finally:
            conn.close()

class EnhancedRuntimeSystem:
    def __init__(self, config: EmbeddingConfig = None):
        self.config = config or EmbeddingConfig()
        self.runtime_state = RuntimeState()
        self.ollama_client = OllamaClient()
        self.documents: List[Document] = []
        self.document_embeddings: Dict[str, array.array] = {}
        self.clusters: Dict[int, List[str]] = defaultdict(list)

    async def add_document(self, content: str, metadata: Dict = None) -> Optional[Document]:
        try:
            embedding = await self.ollama_client.generate_embedding(content)
            if embedding:
                doc = Document(content=content, embedding=embedding, metadata=metadata)
                self.documents.append(doc)
                
                # Store embedding as array
                self.document_embeddings[doc.uuid] = array.array(
                    self.config.get_format_char(), 
                    embedding
                )
                
                # Assign to cluster
                cluster_id = self._assign_to_cluster(doc.uuid)
                self.clusters[cluster_id].append(doc.uuid)
                
                # Update Merkle tree
                await self._update_merkle_state()
                
                return doc
        except Exception as e:
            logger.error(f"Error adding document: {e}")
        return None

    def _assign_to_cluster(self, doc_uuid: str) -> int:
        if not self.clusters:
            return 0
            
        embedding = self.document_embeddings[doc_uuid]
        best_cluster = 0
        best_similarity = -1
        
        for cluster_id, doc_uuids in self.clusters.items():
            if doc_uuids:
                cluster_embedding = self._get_cluster_centroid(cluster_id)
                similarity = self._cosine_similarity(embedding, cluster_embedding)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_cluster = cluster_id
                    
        return best_cluster

    def _get_cluster_centroid(self, cluster_id: int) -> array.array:
        doc_uuids = self.clusters[cluster_id]
        if not doc_uuids:
            return array.array(self.config.get_format_char(), [0.0] * self.config.dimensions)
            
        embeddings = [self.document_embeddings[uuid] for uuid in doc_uuids]
        centroid = array.array(self.config.get_format_char(), [0.0] * self.config.dimensions)
        
        for emb in embeddings:
            for i in range(len(centroid)):
                centroid[i] += emb[i]
                
        for i in range(len(centroid)):
            centroid[i] /= len(embeddings)
            
        return centroid

    def _cosine_similarity(self, v1: array.array, v2: array.array) -> float:
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(x * x for x in v1))
        norm2 = math.sqrt(sum(x * x for x in v2))
        return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0

    async def _update_merkle_state(self):
        """Update the Merkle tree with current system state"""
        system_state = {
            'timestamp': datetime.utcnow().isoformat(),
            'document_count': len(self.documents),
            'cluster_count': len(self.clusters),
            'config': self.config.__dict__
        }
        
        # Create new Merkle node for current state
        state_node = MerkleNode(system_state)
        
        # Add document nodes
        for doc in self.documents:
            doc_node = MerkleNode({
                'uuid': doc.uuid,
                'content': doc.content,
                'metadata': doc.metadata
            })
            state_node.add_child(doc_node)
        
        self.runtime_state.merkle_root = state_node
        self.runtime_state.state_history.append(state_node.hash)
        
        # Save state to disk
        await self._save_state()

    async def _save_state(self):
        """Save enhanced state to disk"""
        previous_state = self._load_latest_previous_state()
        
        state_data = {
            'root_hash': self.runtime_state.merkle_root.hash,
            'parent_hash': previous_state['root_hash'] if previous_state else None,
            'version': '0.1.0',
            'timestamp': datetime.utcnow().isoformat(),
            'state_sequence': len(self.runtime_state.state_history),
            
            'merkle_metadata': self._generate_merkle_metadata(),
            'navigation': self._generate_navigation_data(previous_state),
            'index': self._generate_index_data(),
            'state_deltas': self._calculate_state_deltas(previous_state),
            'performance_metrics': self._collect_performance_metrics(),
            
            # Existing data
            'documents': [...],
            'embeddings': {...},
            'clusters': {...},
            'state_history': self.runtime_state.state_history
        }
        
        # Save with nibble-wise organization
        path = Path('states') / self.runtime_state.merkle_root.hash[:2] / self.runtime_state.merkle_root.hash[2:4]
        path.mkdir(parents=True, exist_ok=True)
        with open(path / f"{self.runtime_state.merkle_root.hash}.json", 'w') as f:
            json.dump(state_data, f, indent=2)

    def _generate_merkle_metadata(self):
        """Generate metadata about the Merkle tree structure"""
        def traverse_tree(node, level=0, acc=None):
            if acc is None:
                acc = defaultdict(list)
            acc[f"level_{level}"].append(node.hash)
            for child in node.children:
                traverse_tree(child, level + 1, acc)
            return acc

        node_references = traverse_tree(self.runtime_state.merkle_root)
        return {
            'tree_height': len(node_references),
            'total_nodes': sum(len(nodes) for nodes in node_references.values()),
            'node_references': dict(node_references)
        }

    async def query(self, query_text: str, top_k: int = 3) -> Dict:
        try:
            query_embedding = await self.ollama_client.generate_embedding(query_text)
            if not query_embedding:
                return {'error': 'Failed to generate query embedding'}

            query_array = array.array(self.config.get_format_char(), query_embedding)
            
            # Find similar documents
            similarities = []
            for doc in self.documents:
                doc_embedding = self.document_embeddings[doc.uuid]
                similarity = self._cosine_similarity(query_array, doc_embedding)
                similarities.append((doc, similarity))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_docs = similarities[:top_k]
            
            # Generate response using context
            context = "\n".join([doc.content for doc, _ in top_docs])
            prompt = f"Context:\n{context}\n\nQuery: {query_text}\n\nResponse:"
            response = await self.ollama_client.generate_response(prompt)
            
            return {
                'query': query_text,
                'response': response,
                'similar_documents': [
                    {
                        'content': doc.content,
                        'similarity': score,
                        'metadata': doc.metadata
                    }
                    for doc, score in top_docs
                ]
            }
        except Exception as e:
            logger.error(f"Query error: {e}")
            return {'error': str(e)}
class FeedbackLoop:
    def __init__(self, system: EnhancedRuntimeSystem):
        self.system = system

    async def evaluate_documents(self):
        """A simple feedback loop to score and label documents"""
        scores = {}
        
        for doc in self.system.documents:
            score = 0
            # Basic heuristics - can be replaced or expanded with more sophisticated methods
            if "function" in doc.content.lower():
                score += 1
            if len(doc.content) > 1000:
                score += 1
            if "import" in doc.content.lower():
                score += 1
            
            # Store the score with associated UUID
            scores[doc.uuid] = score
        
        return scores

    async def apply_feedback(self, scores: Dict[str, int], threshold: int = 2):
        """Label and adjust documents based on scores and feedback"""
        for doc_uuid, score in scores.items():
            doc = next(doc for doc in self.system.documents if doc.uuid == doc_uuid)

            if score >= threshold:
                doc.metadata['label'] = 'High Relevance'
            else:
                doc.metadata['label'] = 'Low Relevance'
            
            logger.info(f"Document {doc_uuid} labeled as: {doc.metadata['label']}")

async def main_feedback_loop():
    # Presuming system is an instance of EnhancedRuntimeSystem with documents
    feedback_loop = FeedbackLoop(system)
    
    scores = await feedback_loop.evaluate_documents()
    await feedback_loop.apply_feedback(scores)

@dataclass
class Document:
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict = field(default_factory=dict)

class Cache:
    def __init__(self, file_name: str = '.request_cache.json'):
        self.file_name = file_name
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.file_name):
            with open(self.file_name, 'r') as f:
                return json.load(f)
        return {}
    
    def save_cache(self):
        with open(self.file_name, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)

    def set(self, key: str, value: Any):
        self.cache[key] = value
        self.save_cache()

class SyntaxKernel:
    def __init__(self, model_host: str, model_port: int):
        self.model_host = model_host
        self.model_port = model_port
        self.cache = Cache()

    async def fetch_from_api(self, path: str, data: Dict) -> Optional[Dict]:
        cache_key = hashlib.sha256(json.dumps(data).encode()).hexdigest()
        cached_response = self.cache.get(cache_key)

        if cached_response:
            logger.info(f"Cache hit for {cache_key}")
            return cached_response

        logger.info(f"Querying API for {cache_key}")
        conn = http.client.HTTPConnection(self.model_host, self.model_port)

        try:
            headers = {'Content-Type': 'application/json'}
            conn.request("POST", path, json.dumps(data), headers)
            response = conn.getresponse()
            
            # Read the response body
            response_data = response.read().decode('utf-8')
            
            # Split response by newlines in case of streaming response
            json_objects = [json.loads(line) for line in response_data.strip().split('\n') if line.strip()]
            
            if json_objects:
                # Take the last complete response
                result = json_objects[-1]
                self.cache.set(cache_key, result)
                return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding failed: {str(e)}")
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
        finally:
            conn.close()
        return None

    async def analyze_token(self, token: str) -> str:
        if len(token.split()) > 5:
# ===================================================---------------------------------------------------
            response = await self.fetch_from_api("/api/analyze", {"model": "gemma2", "query": token})
# ===================================================---------------------------------------------------
            return response.get('response', '') if response else "Analysis unavailable."
        return token

class LocalRAGSystem:
    def __init__(self, host: str = "localhost", port: int = 11434):
        self.host = host
        self.port = port
        self.documents: List[Document] = []
        self.syntax_kernel = SyntaxKernel(host, port)

    async def generate_embedding(self, text: str) -> List[float]:
        response = await self.syntax_kernel.fetch_from_api("/api/embeddings", {
            "model": "nomic-embed-text",
            "prompt": text
        })
        
        if not response or not isinstance(response, dict):
            logger.error(f"Failed to generate embedding for text: {text[:50]}...")
            return []
            
        embedding = response.get('embedding', [])
        if not embedding:
            logger.error(f"No embedding found in response for text: {text[:50]}...")
        return embedding

    async def add_document(self, content: str, metadata: Dict = None) -> Document:
        if not content.strip():
            logger.warning("Attempting to add empty document")
            return None
            
        embedding = await self.generate_embedding(content)
        if not embedding:
            logger.warning(f"Failed to generate embedding for document: {content[:50]}...")
            return None
            
        doc = Document(content=content, embedding=embedding, metadata=metadata or {})
        self.documents.append(doc)
        return doc
    
    async def remove_document(self, content: str) -> bool:
        self.documents = [doc for doc in self.documents if doc.content != content]
        return True
        
    async def clear_documents(self):
        self.documents.clear()
        
    async def get_documents_by_topic(self, topic: str) -> List[Document]:
        return [doc for doc in self.documents if doc.metadata.get('topic') == topic]
        
    async def import_documents_from_file(self, filepath: str):
        with open(filepath, 'r') as f:
            for line in f:
                content = line.strip()
                if content:
                    await self.add_document(content, {"type": "imported"})

    def calculate_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        norm1 = sum(a * a for a in emb1) ** 0.5
        norm2 = sum(b * b for b in emb2) ** 0.5
        return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0

    async def search_similar(self, query: str, top_k: int = 3) -> List[Tuple[Document, float]]:
        query_embedding = await self.generate_embedding(query)
        similarities = [(doc, self.calculate_similarity(query_embedding, doc.embedding))
                        for doc in self.documents if doc.embedding is not None]
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    async def query(self, query: str, top_k: int = 3) -> Dict:
        similar_docs = await self.search_similar(query, top_k)
        context = "\n".join(doc.content for doc, _ in similar_docs)
        
        # Combine query with context for better results
        prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        
        response = await self.syntax_kernel.fetch_from_api("/api/generate", {
            "model": "gemma2",
            "prompt": prompt,
            "stream": False  # Add this if your API supports it
        })
        
        response_text = 'Unable to generate response.'
        if response and isinstance(response, dict):
            response_text = response.get('response', response_text)
        
        return {
            'query': query,
            'response': response_text,
            'similar_documents': [
                {
                    'content': doc.content,
                    'similarity': score,
                    'metadata': doc.metadata
                } for doc, score in similar_docs
            ]
        }
 
    async def evaluate_response(self, query: str, response: str, similar_docs: List[Dict]) -> float:
        # Simple relevance score based on similarity to retrieved documents
        response_embedding = await self.generate_embedding(response)
        
        # Calculate average similarity between response and retrieved documents
        similarities = []
        for doc in similar_docs:
            doc_embedding = await self.generate_embedding(doc['content'])
            similarity = self.calculate_similarity(response_embedding, doc_embedding)
            similarities.append(similarity)
            
        return sum(similarities) / len(similarities) if similarities else 0.0

    def clear_cache(self):
        self.syntax_kernel.cache = Cache()
        
    def set_cache_policy(self, max_age: int = None, max_size: int = None):
        # Implement cache management policies
        pass

async def interactive_mode(rag: LocalRAGSystem):
    print("Enter your questions (type 'exit' to quit):")
    while True:
        query = input("\nYour question: ").strip()
        if query.lower() == 'exit':
            break
            
        result = await rag.query(query)
        print("\nResponse:", result['response'])
        print("\nRelevant Sources:")
        for doc in result['similar_documents']:
            print(f"- [{doc['metadata']['topic']}] {doc['content']} (similarity: {doc['similarity']:.3f})")

async def main():
    rag = LocalRAGSystem()
    await rag.add_document("Neural networks are computing systems inspired by biological neural networks.", {"type": "definition", "topic": "AI"})
    # Import initial knowledge base
    await rag.import_documents_from_file('README.md')

    # await interactive_mode(rag)
    
    documents = [
        ("Embeddings are dense vector representations of data in a high-dimensional space.", 
         {"type": "definition", "topic": "NLP"}),
        ("RAG (Retrieval Augmented Generation) combines retrieval and generation for better responses.", 
         {"type": "definition", "topic": "AI"}),
        ("Transformers are a type of neural network architecture that uses self-attention mechanisms.",
         {"type": "technical", "topic": "AI"}),
        ("Vector databases optimize similarity search for embedding-based retrieval.",
         {"type": "technical", "topic": "Databases"}),
    ]
    
    for content, metadata in documents:
        await rag.add_document(content, metadata)

    queries = ["What are neural networks?", "Explain embeddings in simple terms", "How does RAG work?"]

    for query in queries:
        print(f"\nQuery: {query}")
        result = await rag.query(query)
        print("\nResponse:", result['response'])
        print("\nSimilar Documents:")
        for doc in result['similar_documents']:
            print(f"- Score: {doc['similarity']:.3f}")
            print(f"  Content: {doc['content']}")
            print(f"  Metadata: {doc['metadata']}")
    query = "Explain the relationship between embeddings and neural networks"
    result = await rag.query(query)
    
    # Evaluate response quality
    relevance_score = await rag.evaluate_response(
        query, 
        result['response'], 
        result['similar_documents']
    )
    print(f"Response relevance score: {relevance_score:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
    # Initialize system
    config = EmbeddingConfig(
        dimensions=768,
        precision='float32',
        cluster_count=8,
        cache_path='runtime_cache.json'
    )
    
    system = EnhancedRuntimeSystem(config)

    asyncio.run(main_feedback_loop())
#------------------------------------------------------------------------------
