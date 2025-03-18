from __future__ import annotations
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import decimal
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
# Create a logger with the name of the module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a formatter for log messages
formatter = logging.Formatter('[%(levelname)s]%(asctime)s||%(name)s: %(message)s', datefmt='%Y-%m-%d~%H:%M:%S%z')

# Create a console handler and add it to the logger
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create a file handler and add it to the logger
logs_dir = Path(__file__).resolve().parent / 'logs'
logs_dir.mkdir(exist_ok=True)
file_handler = RotatingFileHandler(logs_dir / 'app.log', maxBytes=10485760, backupCount=10)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Log a message indicating that logging has been initialized
logger.info('Logging initialized from %s', __file__)

#------------------------------------------------------------------------------
# Type Definitions
#------------------------------------------------------------------------------
"""
Type Definitions for Morphological Source Code.

These type definitions establish the foundational elements of the MSC framework, 
enabling the representation of various constructs as first-class citizens.

- T: Represents Type structures (static).
- V: Represents Value spaces (dynamic).
- C: Represents Computation spaces (transformative).

The relationships between these types are crucial for maintaining the 
nominative invariance across transformations.

1. **Identity Preservation (T)**: The type structure remains consistent across transformations.
2. **Content Preservation (V)**: The value space is dynamically maintained, allowing for fluid data manipulation.
3. **Behavioral Preservation (C)**: The computation space is transformative, enabling the execution of operations that modify the state of the system.

Homoiconism dictates that, upon runtime validation, all objects are code and data. 
To facilitate this, we utilize first-class functions and a static typing system.

This maps perfectly to the three aspects of nominative invariance:

- Identity preservation, T: Type structure (static)
- Content preservation, V: Value space (dynamic)
- Behavioral preservation, C: Computation space (transformative)

[[T (Type) ↔ V (Value) ↔ C (Callable)]] == 'quantum infodynamics, a tripartite element; our Particle()(s)'

Meta-Language (High Level)
  ↓ [First Collapse - Compilation]
Intermediate Form (Like a quantum superposition)
  ↓ [Second Collapse - Runtime]
Executed State (Measured Reality)

What's conserved across these transformations:

- Nominative relationships
- Information content
- Causal structure
- Computational potential

The type system forms the "boundary" theory.
The runtime forms the "bulk" theory.

The homoiconic property ensures they encode the same information. The holoiconic property enables:

- States as quantum superpositions
- Computations as measurements
- Types as boundary conditions
- Runtime as bulk geometry
"""

# Core type variables representing the three fundamental symmetries
T = TypeVar('T')  # Type structure (static)
# # T for TypeVar, V for ValueVar. Homoicons are T+V, 'Particle()(s)' are all-three
V = TypeVar('V')  # Value space (dynamic)
C = TypeVar('C', bound=Callable)  # Computation space (transformative)
# Callable, 'C' TypeVar(s) include Foreign Function Interface, git and (power)shell, principally

DataType = StrEnum('DataType', 'INTEGER FLOAT STRING BOOLEAN NONE LIST TUPLE') # 'T' vars (stdlib)
PyType = StrEnum('ModuleType', 'FUNCTION CLASS MODULE OBJECT') 
# PyType: first class functions applies to objects, classes and even modules, 'C' vars which are not FFI(s)

AccessLevel = StrEnum('AccessLevel', 'READ WRITE EXECUTE ADMIN USER')
QuantumState = StrEnum('QuantumState', ['SUPERPOSITION', 'ENTANGLED', 'COLLAPSED', 'DECOHERENT'])

"""
Particle()(s) are a wrapper that can represent any Python object, including values, methods, functions, and classes.
"""
class ParticleType(Enum):
    FERMION = auto()
    BOSON = auto()

class QuantumNumbers(NamedTuple):
    n: int  # Principal quantum number
    l: int  # Azimuthal quantum number
    m: int  # Magnetic quantum number
    s: float   # Spin quantum number

class QuantumNumber:
    def __init__(self, hilbert_space: HilbertSpace):
        self.hilbert_space = hilbert_space
        self.amplitudes = [complex(0, 0)] * hilbert_space.dimension
        self._quantum_numbers = None

    @property
    def quantum_numbers(self):
        return self._quantum_numbers

    @quantum_numbers.setter
    def quantum_numbers(self, numbers: QuantumNumbers):
        n, l, m, s = numbers
        if self.hilbert_space.is_fermionic():
            # Fermionic quantum number constraints
            if not (n > 0 and 0 <= l < n and -l <= m <= l and s in (-0.5, 0.5)):
                raise ValueError("Invalid fermionic quantum numbers")
        elif self.hilbert_space.is_bosonic():
            # Bosonic quantum number constraints
            if not (n >= 0 and l >= 0 and m >= 0 and s == 0):
                raise ValueError("Invalid bosonic quantum numbers")
        self._quantum_numbers = numbers

class MathProtocol(Protocol):
    """
    Base protocol for mathematical operations.
    
    This serves as an abstract base class for mathematical objects that support 
basic arithmetic and other operations.
    """

    def __init__(self, *args, **kwargs):
        pass

    def __add__(self, other: 'MathProtocol') -> 'MathProtocol':
        """
        Add/Commute two mathematical objects together.
        """
        raise NotImplementedError

    def __sub__(self, other: 'MathProtocol') -> 'MathProtocol':
        """
        Subtract two mathematical objects.
        """
        raise NotImplementedError

_decimal_places = decimal.getcontext()

"""
Python objects are implemented as C structures.

```c
typedef struct _object {
    Py_ssize_t ob_refcnt;
    PyTypeObject *ob_type;
} PyObject;
```

Everything in Python is an object, and every object has a type. 
The type of an object is a class. Even the type class itself is an instance of type. 
Functions defined within a class become method objects when accessed through an instance of the class.

Functions are instances of the function class.
Methods are instances of the method class (which wraps functions).
Both function and method are subclasses of object.

Homoiconism dictates the need for a way to represent all Python constructs as first-class citizens (fcc):

- Functions
- Classes
- Control structures
- Operations
- Primitive values
"""

"""
Nominative "true OOP" (SmallTalk) and my specification demands code as data and value as logic, structure.

The Particle(), our polymorph of object and fcc-apparent at runtime, always represents the literal source code
which makes up their logic and possesses the ability to be stateful source code data structure.

Homoiconistic morphological source code displays 'modified quine' behavior
within a validated runtime, if and only if the valid Python interpreter
has r/w/x permissions to the source code file and some method of writing
state to the source code file is available.

Any interruption of the `__exit__` method or misuse of `__enter__` will result in a runtime error.
"""

"""
AP (Availability + Partition Tolerance, with lazy/halting consistentcy):

A system that prioritizes availability and partition tolerance may use a distributed architecture with eventual consistency (e.g., Cassandra or Riak).
This ensures that the system is always available (availability), even in the presence of network partitions (partition tolerance).
However, the system may sacrifice consistency, as nodes may have different views of the data (no consistency).

A homoiconic piece of source code is eventually consistent, assuming it is able to be re-instantiated.

[ Runtime Node A ] ----[ Entanglement ]---- [ Runtime Node B ]
      |                                   |
   [ Quined State A ]          [ Quined State B ]
      |                                   |
[ Probabilistic Resolution Network (PRN) ]
"""