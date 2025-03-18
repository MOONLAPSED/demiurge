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
try:
    from src.__init__ import __all__
    if not __all__:
        __all__ = []
    else:
        __all__ += __file__
except ImportError:
    __all__ = []
    __all__ += __file__
IS_WINDOWS = os.name == 'nt'
IS_POSIX = os.name == 'posix'
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

benchmark_profiler = cProfile.Profile()

@lambda _: _()
def FireFirst() -> None:
    """Function that fires on import."""
    PORT = 8421  # Changed from 8420 to avoid conflict
    try:
        available_port = find_available_port(PORT)
        logger.info(f"Using port: {available_port}")
        print(f'func you')
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        return True

class CommandBenchmark:
    """Benchmark execution of a command"""
    def __init__(self, command: List[str], iterations: int = 10):
        self.command = command
        self.iterations = iterations
        self.results: List[float] = []
    def run(self) -> float:
        best = sys.maxsize
        for _ in range(self.iterations):

class SystemProfiler:
    """Handles system profiling and performance measurements"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'SystemProfiler':
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self) -> None:
        self.profiler = cProfile.Profile()
        self.start_time = time.monotonic()
        
    def start(self) -> None:
        self.profiler.enable()
        
    def stop(self) -> str:
        self.profiler.disable()
        s = StringIO()
        ps = pstats.Stats(self.profiler, stream=s).sort_stats('cumulative')
        ps.print_stats()
        return s.getvalue()

class ProcessExecutor:
    """Platform-independent process execution"""
    @staticmethod
    def _windows_run_command(command, timeout, env):
        from ctypes import windll, wintypes
        
        # Optimize process priority - using Windows ABOVE_NORMAL_PRIORITY_CLASS
        def set_process_priority():
            windll.kernel32.SetPriorityClass(
                wintypes.HANDLE(-1), 
                0x00008000  # ABOVE_NORMAL_PRIORITY_CLASS
            )

        def wrun_command(command, timeout=None, env=None):
            # Increase buffer sizes for better performance
            BUFFER_SIZE = 65536  # 64KB buffer
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
                shell=True,
                env=env,
                bufsize=BUFFER_SIZE  # Set larger buffer
            )
            
            # Set higher priority for the subprocess
            set_process_priority()
            
            # Use memoryview for zero-copy buffering
            def read_stream(stream):
                buffer = []
                while True:
                    chunk = stream.read1(BUFFER_SIZE)
                    if not chunk:
                        break
                    buffer.append(chunk)
                return b''.join(buffer).decode()
                
            stdout = read_stream(process.stdout)
            stderr = read_stream(process.stderr)
            
            return_code = process.wait(timeout=timeout)
            return stdout, stderr, return_code

        try:
            stdout, stderr, status = wrun_command(command, timeout=timeout, env=env)
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            print("STATUS:", status, '\n', '_' * 80)
            return stdout, stderr, status
        except TimeoutError as e:
            print(e)
            raise
        except Exception as e:
            print(e)
            raise
    @staticmethod
    def _posix_run_command(command, timeout, env):
        import resource
        
        # Set process priority using nice value (-20 to 19, lower is higher priority)
        def set_process_priority():
            try:
                os.nice(-10)  # Higher priority but not maximum
            except PermissionError:
                pass
                
        def run_command(command, timeout=None, env=None):
            BUFFER_SIZE = 65536  # 64KB buffer
            
            # Set resource limits for better performance
            resource.setrlimit(resource.RLIMIT_NOFILE, (4096, 4096))
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
                shell=True,
                env=env,
                bufsize=BUFFER_SIZE,
                preexec_fn=set_process_priority
            )
            
            # Use memoryview for efficient reading
            stdout, stderr = process.communicate(timeout=timeout)
            return stdout.decode(), stderr.decode(), process.returncode
        try:
            stdout, stderr, status = run_command(command, timeout=timeout, env=env)
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            print("STATUS:", status, '\n', '_' * 80)
            return stdout, stderr, status  # Add return statement
        except TimeoutError as e:
            print(e)
            raise
        except Exception as e:
            print(e)
            raise
    @staticmethod
    def run_command(command: List[str], timeout: Optional[float] = None, 
                   env: Optional[Dict[str, str]] = None) -> Tuple[str, str, int]:
        """Platform-independent command execution"""
        if IS_WINDOWS:
            return ProcessExecutor._windows_run_command(command, timeout, env)
        return ProcessExecutor._posix_run_command(command, timeout, env)

class Benchmark:
    """Command benchmarking utility"""
    def __init__(self, command: List[str], iterations: int = 10):
        self.command = command
        self.iterations = iterations
        self.results: List[float] = []
        self.profiler = SystemProfiler()
    def run(self) -> float:
        self.profiler.start()
        best = sys.maxsize
        for _ in range(self.iterations):
            t0 = time.monotonic()
            ProcessExecutor.run_command(self.command)
            t1 = time.monotonic()
            duration = t1 - t0
            self.results.append(duration)
            best = min(best, duration)
            print(f'{duration:.3f}s')
        profile_data = self.profiler.stop()
        print('_' * 80)
        print(f'Best of {self.iterations}: {best:.3f}s')
        print('Profile data:')
        print(profile_data)
        return best

def generate_ansi_color(c: str) -> str:
    """Generate an ANSI escape code for colored text"""
    colors = {
        'reset': '\033[0m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m'
    }
    return colors.get(c.lower(), colors['reset'])

@dataclass
class BenchmarkReport:
    command: str
    best_time: float
    iterations: int
    
    def __repr__(self):
        command_color = generate_ansi_color('cyan')
        timing_color = generate_ansi_color('green')
        title_color = generate_ansi_color('yellow')
        reset_color = generate_ansi_color('reset')

        report = f"{title_color}Benchmark Report:{reset_color}\n"
        report += f"{command_color}Command:{reset_color} {self.command}\n"
        report += f"{timing_color}Best time:{reset_color} {self.best_time:.3f}s over {self.iterations} iterations\n"
        return report

@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    returncode: int

    def __repr__(self):
        color_stdout = generate_ansi_color('green')
        color_stderr = generate_ansi_color('red')
        color_return = generate_ansi_color('cyan')
        reset_color = generate_ansi_color('reset')

        output = f"{color_stdout}STDOUT:{reset_color}\n{self.stdout}\n"
        output += f"{color_stderr}STDERR:{reset_color}\n{self.stderr}\n"
        output += f"{color_return}RETURN CODE:{reset_color} {self.returncode}\n"
        return output

def main() -> int:
    parser = argparse.ArgumentParser(description='Benchmark command execution')
    parser.add_argument('-n', '--num', type=int, default=10,
                        help="Number of iterations")
    parser.add_argument('cmd', nargs=argparse.REMAINDER, help="Command to execute")
    args = parser.parse_args()
    
    if not args.cmd:
        parser.error("Command is required")

    # Remove the '--' separator if it exists
    if args.cmd[0] == '--':
        command = args.cmd[1:]
    else:
        command = args.cmd

    # Simulate benchmark execution
    # For demonstration, using fake time measurements; replace with actual benchmarking logic
    benchmark = Benchmark(command, args.num)
    best_time = benchmark.run()  # this should return the best time from the Benchmark class


    # Demonstrate execution result output
    stdout, stderr, returncode = ProcessExecutor.run_command(command)  # this should be a real execution
    execution_result = ExecutionResult(stdout=stdout, stderr=stderr, returncode=returncode)
    # print(execution_result.__dict__)

    benchmark_report = BenchmarkReport(command=' '.join(command), best_time=best_time, iterations=args.num)
    print(benchmark_report)

    return 0

if __name__ == "__main__":
  # Try:
  # uv run .\src\simple\benchmark.py -- python -c "print('hello')"
  # python .\src\simple\benchmark.py -- python src/__init__.py arg1  
  sys.exit(main())
