#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations
#------------------------------------------------------------------------------
# Standard Library Imports - 3.13 std libs **ONLY**
#------------------------------------------------------------------------------
import re
import os
import dis
import sys
import ast
import time
import site
import mmap
import json
import uuid
import cmath
import errno
import shlex
import socket
import struct
import shutil
import pickle
import signal
import ctypes
import pstats
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
from math import sqrt
from array import array
from io import StringIO
from pathlib import Path
from datetime import datetime
from threading import Thread
from queue import Queue, Empty
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from collections.abc import Iterable, Mapping
from concurrent.futures import ThreadPoolExecutor
from enum import Enum, auto, IntEnum, StrEnum, Flag
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
profiler = cProfile.Profile()
@lambda _: _()
def FireFirst() -> None:
    profiler.enable()
    print(f'func you')
    return True
# fires as soon as python sees it.
if IS_WINDOWS:
    from ctypes import windll
    from ctypes import wintypes
    from ctypes.wintypes import HANDLE, DWORD, LPWSTR, LPVOID, BOOL
    from pathlib import PureWindowsPath
    def set_process_priority(priority: int):
        windll.kernel32.SetPriorityClass(wintypes.HANDLE(-1), priority)
    WINDOWS_SANDBOX_DEFAULT_DESKTOP = Path(PureWindowsPath(r'C:\Users\WDAGUtilityAccount\Desktop'))
    set_process_priority(0x00000020)
    def wread_stream(stream, queue):
        """Read lines from a stream and push them to a queue."""
        for line in iter(stream.readline, b''):
            queue.put(line.decode())
        stream.close()
    def wrun_command(command, timeout=None, env=None):
        """
        Executes a command, capturing stdout and stderr with optional timeout.
        Args:
            command (list): Command and arguments as a list, e.g., ['cmd', '/c', 'dir']
            timeout (float): Timeout in seconds for the command to execute
            env (dict): Environment variables to set for the command
        Returns:
            tuple: stdout (str), stderr (str), exit_status (int)
        """
        # Start the subprocess
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,  # Read binary streams
            env=env
        )
        # Queues for communication
        stdout_queue = Queue()
        stderr_queue = Queue()
        # Threads to read stdout and stderr
        stdout_thread = Thread(target=wread_stream, args=(process.stdout, stdout_queue))
        stderr_thread = Thread(target=wread_stream, args=(process.stderr, stderr_queue))
        stdout_thread.start()
        stderr_thread.start()
        start_time = time.time()
        try:
            while True:
                if timeout and (time.time() - start_time) > timeout:
                    process.send_signal(signal.CTRL_BREAK_EVENT if os.name == 'nt' else signal.SIGKILL)
                    raise TimeoutError(f"Command '{command[0]}' timed out after {timeout} seconds")
                # Check if process has completed
                ret_code = process.poll()
                if ret_code is not None:
                    break
                time.sleep(0.01)  # Prevent busy-waiting
        finally:
            # Ensure threads finish
            stdout_thread.join()
            stderr_thread.join()
            # Close the process
            process.stdout.close()
            process.stderr.close()
        # Collect output from queues
        stdout = ''.join(iter(lambda: stdout_queue.get_nowait() if not stdout_queue.empty() else '', ''))
        stderr = ''.join(iter(lambda: stderr_queue.get_nowait() if not stderr_queue.empty() else '', ''))
        return stdout, stderr, process.returncode
    try:
        stdout, stderr, status = wrun_command(['cmd', '/c', 'dir'], timeout=5)
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        print("STATUS:", status, '\n', '_' * 80)
    except TimeoutError as e:
        print(e)
    except Exception as e:
        print(e)
elif IS_POSIX:
    import resource
    import fcntl
    def set_process_priority(priority: int):
        try:
            os.nice(priority)
        except PermissionError:
            print("Warning: Unable to set process priority. Running with default priority.")
    def run_command(command, timeout=None, env=None):
        """
        Executes a command, capturing stdout and stderr with optional timeout.
        Args:
            command (list): Command and arguments as a list, e.g., ['ls', '-l']
            timeout (float): Timeout in seconds for the command to execute
            env (dict): Environment variables to set for the command
        Returns:
            tuple: stdout (str), stderr (str), exit_status (int)
        """
        r_stdout, w_stdout = os.pipe()
        r_stderr, w_stderr = os.pipe()
        pid = os.fork()
        if pid == 0:  # Child process
            os.close(r_stdout)
            os.close(r_stderr)
            os.dup2(w_stdout, 1)
            os.dup2(w_stderr, 2)
            os.close(w_stdout)
            os.close(w_stderr)
            # Execute the command with optional environment
            try:
                if env:
                    os.execvpe(command[0], command, env)
                else:
                    os.execvp(command[0], command)
            except Exception as e:
                print(f"Execution failed: {e}", file=os.fdopen(2, 'w'))
                os._exit(1)
        else:  # Parent process
            os.close(w_stdout)
            os.close(w_stderr)
            fcntl.fcntl(r_stdout, fcntl.F_SETFL, fcntl.fcntl(r_stdout, fcntl.F_GETFL) | os.O_NONBLOCK)
            fcntl.fcntl(r_stderr, fcntl.F_SETFL, fcntl.fcntl(r_stderr, fcntl.F_GETFL) | os.O_NONBLOCK)
            stdout_output = []
            stderr_output = []
            start_time = time.time()
            try:
                while True:
                    if timeout and (time.time() - start_time) > timeout:
                        os.kill(pid, signal.SIGKILL)
                        raise TimeoutError(f"Command '{command[0]}' timed out after {timeout} seconds")
                    # Read from stdout
                    try:
                        stdout_chunk = os.read(r_stdout, 4096)
                        if stdout_chunk:
                            stdout_output.append(stdout_chunk.decode())
                    except OSError as e:
                        if e.errno != errno.EAGAIN:
                            raise
                    # Read from stderr
                    try:
                        stderr_chunk = os.read(r_stderr, 4096)
                        if stderr_chunk:
                            stderr_output.append(stderr_chunk.decode())
                    except OSError as e:
                        if e.errno != errno.EAGAIN:
                            raise
                    # Check if child has exited
                    pid_exit, status = os.waitpid(pid, os.WNOHANG)
                    if pid_exit == pid:
                        break
                    time.sleep(0.01)  # Small sleep to avoid busy-waiting
            finally:
                os.close(r_stdout)
                os.close(r_stderr)
            # Convert output lists to strings
            stdout = ''.join(stdout_output)
            stderr = ''.join(stderr_output)
            return stdout, stderr, os.WEXITSTATUS(status) if pid_exit == pid else -1
        try:
            stdout, stderr, status = run_command(['ls', '-l'], timeout=5)
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            print("STATUS:", status, '\n', '_' * 80)
        except TimeoutError as e:
            print(e)
        except Exception as e:
            print(e)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--num', type=int, default=10, help="Number of iterations")
    parser.add_argument('cmd', nargs='+', help="Command to execute")
    args = parser.parse_args()
    best: float = sys.maxsize
    for _ in range(args.num):
        t0 = time.monotonic()
        subprocess.call(args.cmd)
        t1 = time.monotonic()
        best = min(best, t1 - t0)
        print(f'{t1 - t0:.3f}s', end=' \n')
        # appends the time to the platform-specific IF_POSIX/IF_WINDOWS code
    print('_' * 80)
    mreturn = print(f'best of {args.num}: {best:.3f}s')
    return mreturn

profiler.disable()
# Extract profiling data
s = StringIO()
sortby = 'cumulative'
ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
ps.print_stats()
profile_data = s.getvalue()
profile_data = profile_data.replace('\\', '').replace('/', '')
profile_data = profile_data.rstrip()
print(profile_data)
print('_' * 80)

if __name__ == "__main__":
    sys.exit(main())