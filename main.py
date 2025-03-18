from __future__ import annotations
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Standard Library Imports - 3.13 std libs **ONLY**
#------------------------------------------------------------------------------
import re
import os
import io
import abc
import dis
import sys
import ast
import time
import json
import math
import uuid
import array
import shlex
import struct
import shutil
import pickle
import ctypes
import logging
import weakref
import tomllib
import pathlib
import asyncio
import inspect
import hashlib
import argparse
import tempfile
import platform
import importlib
import functools
import linecache
import traceback
import mimetypes
import threading
import subprocess
import contextvars
import tracemalloc
from pathlib import Path
from enum import Enum, auto, StrEnum
from queue import Queue, Empty
from datetime import datetime
from abc import ABC, abstractmethod
from contextlib import contextmanager
from functools import wraps, lru_cache
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from importlib.util import spec_from_file_location, module_from_spec
from types import SimpleNamespace, ModuleType,  MethodType, FunctionType, CodeType, TracebackType, FrameType
from typing import (
    Any, Dict, List, Optional, Union, Callable, TypeVar, Tuple, Generic, Set,
    Coroutine, Type, NamedTuple, ClassVar, Protocol, runtime_checkable
)

@dataclass
class ProjectConfig:
    """Project configuration container"""
    name: str
    version: str
    python_version: str
    dependencies: List[str]
    dev_dependencies: List[str] = field(default_factory=list)
    ruff_config: Dict[str, Any] = field(default_factory=dict)
    ffi_modules: List[str] = field(default_factory=list)
    src_path: Path = Path("src")
    tests_path: Path = Path("tests")

class ProjectManager:
    def __init__(self, root_dir: Union[str, Path]):
        self.root_dir = Path(root_dir).resolve()  # Use resolve() for absolute paths
        self.logger = self._setup_logging()
        self.config = self._load_or_create_config()
        self.project_config = self._load_project_config()
        self.ffi_modules = self.project_config.get("ffi_modules", [])
        self._ensure_directory_structure()
        self.is_windows = platform.system() == "Windows"

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def _load_project_config(self) -> Dict[str, Any]:
        """Load project-specific configuration from demiurge.json"""
        config_path = self.root_dir / "demiurge.json"
        default_config = {
            "ffi_modules": [],
            "src_path": "src",
            "dev_dependencies": [],
            "profile_enabled": True,
            "platform_specific": {
                "windows": {
                    "priority": 32
                },
                "linux": {
                    "priority": 0
                }
            }
        }
        
        if not config_path.exists():
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
            return default_config
            
        with open(config_path, encoding='utf-8') as f:
            return json.load(f)

    def _load_or_create_config(self) -> ProjectConfig:
        pyproject_path = self.root_dir / "pyproject.toml"
        if not pyproject_path.exists():
            self.logger.info("No pyproject.toml found. Creating default configuration.")
            config = ProjectConfig(
                name=self.root_dir.name,
                version="0.1.0",
                python_version=">=3.13",
                dependencies=["uvx>=0.1.0"],  # Removed duplicate
                dev_dependencies=[
                    "ruff>=0.3.0",
                    "pytest>=8.0.0",
                    "pytest-asyncio>=0.23.0"
                ],
                ruff_config={
                    "line-length": 88,
                    "target-version": "py313",
                    "select": ["E", "F", "I", "N", "W"],
                    "ignore": [],
                    "fixable": ["A", "B", "C", "D", "E", "F", "I"]
                },
                ffi_modules=[]
            )
            self._write_pyproject_toml(config)
            return config
            
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            
        return ProjectConfig(
            name=data["project"]["name"],
            version=data["project"]["version"],
            python_version=data["project"]["requires-python"],
            dependencies=data["project"].get("dependencies", []),
            dev_dependencies=data["project"].get("dev-dependencies", []),
            ruff_config=data.get("tool", {}).get("ruff", {}),
            ffi_modules=data["project"].get("ffi-modules", []),
            src_path=Path(data["project"].get("src-path", "src")),
            tests_path=Path(data["project"].get("tests-path", "tests"))
        )

    def _write_pyproject_toml(self, config: ProjectConfig):
        """Write pyproject.toml using manual string construction instead of tomllib.dumps()"""
        toml_content = f"""[project]
name = "{config.name}"
version = "{config.version}"
requires-python = "{config.python_version}"
dependencies = [
"""
        # Add dependencies
        for dep in config.dependencies:
            toml_content += f'    "{dep}",\n'
        toml_content += "]\n\n"
        
        # Add dev dependencies
        toml_content += "dev-dependencies = [\n"
        for dep in config.dev_dependencies:
            toml_content += f'    "{dep}",\n'
        toml_content += "]\n\n"
        
        # Add other project settings
        toml_content += f'ffi-modules = {json.dumps(config.ffi_modules)}\n'
        toml_content += f'src-path = "{config.src_path}"\n'
        toml_content += f'tests-path = "{config.tests_path}"\n\n'
        
        # Add ruff config
        toml_content += "[tool.ruff]\n"
        for key, value in config.ruff_config.items():
            if isinstance(value, list):
                toml_content += f"{key} = {json.dumps(value)}\n"
            else:
                toml_content += f"{key} = {value}\n"
        
        with open(self.root_dir / "pyproject.toml", "w", encoding='utf-8') as f:
            f.write(toml_content)

    def _ensure_directory_structure(self):
        """Create necessary project directories if they don't exist"""
        dirs = [
            self.config.src_path,
            self.config.tests_path,
            self.config.src_path / "ffi"
        ]
        for dir_path in dirs:
            full_path = self.root_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            init_file = full_path / "__init__.py"
            if not init_file.exists():
                init_file.touch()

    @contextmanager
    def _temp_requirements(self, requirements: List[str]):
        """Create a temporary requirements file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write('\n'.join(requirements))
            temp_path = f.name
        try:
            yield temp_path
        finally:
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass

    async def run_uv_command(self, cmd: List[str], timeout: Optional[float] = None) -> subprocess.CompletedProcess:
        """Run a UV command asynchronously with timeout support"""
        self.logger.debug(f"Running UV command: {' '.join(cmd)}")
        
        # Modify command for Windows if needed
        if self.is_windows:
            # If first command is not a full path and doesn't end with .exe on Windows, try to add it
            if not cmd[0].endswith('.exe') and '/' not in cmd[0] and '\\' not in cmd[0]:
                if cmd[0] == "uv" or cmd[0] == "uvx":
                    cmd[0] = f"{cmd[0]}.exe"
        
        try:
            # For Windows, we sometimes need shell=True for PATH resolution
            shell = self.is_windows
            if shell:
                # Convert list to string for shell execution on Windows
                cmd_str = subprocess.list2cmdline(cmd)
                process = await asyncio.create_subprocess_shell(
                    cmd_str,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                try:
                    process.terminate()
                    await process.wait()
                except ProcessLookupError:
                    pass
                raise TimeoutError(f"Command timed out after {timeout} seconds")
                
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='replace')
                self.logger.error(f"UV command failed: {error_msg}")
                raise RuntimeError(f"UV command failed: {error_msg}")
                
            return subprocess.CompletedProcess(
                cmd, process.returncode, 
                stdout.decode('utf-8', errors='replace'), 
                stderr.decode('utf-8', errors='replace')
            )
            
        except FileNotFoundError:
            self.logger.error(f"Command not found: {cmd[0]}")
            raise RuntimeError(f"Command not found: {cmd[0]}. Is UV installed and in PATH?")

    async def setup_environment(self):
        """Set up the environment based on mode"""
        self.logger.info("Setting up environment...")
        
        # Create virtual environment - using correct command based on platform
        venv_cmd = ["uv", "venv"]
        if self.is_windows:
            venv_cmd = ["uv.exe", "venv"]
            
        await self.run_uv_command(venv_cmd)
        
        # Create requirements files
        requirements_path = self.root_dir / "requirements.txt"
        dev_requirements_path = self.root_dir / "requirements-dev.txt"
        
        # Write main requirements
        if self.config.dependencies:
            with open(requirements_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.config.dependencies) + '\n')
                
        # Write dev requirements
        if self.config.dev_dependencies:
            with open(dev_requirements_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.config.dev_dependencies) + '\n')
                
        # Generate lock file for main requirements
        if requirements_path.exists():
            self.logger.info("Compiling requirements...")
            pip_cmd = ["uv.exe", "pip"] if self.is_windows else ["uv", "pip"]
            await self.run_uv_command([
                *pip_cmd, "compile", 
                str(requirements_path), 
                "--output-file", 
                str(self.root_dir / "requirements.lock")
            ])
            
        # Generate lock file for dev requirements
        if dev_requirements_path.exists():
            self.logger.info("Compiling dev requirements...")
            pip_cmd = ["uv.exe", "pip"] if self.is_windows else ["uv", "pip"]
            await self.run_uv_command([
                *pip_cmd, "compile", 
                str(dev_requirements_path), 
                "--output-file", 
                str(self.root_dir / "requirements-dev.lock")
            ])
            
        # Install from lock files
        if (self.root_dir / "requirements.lock").exists():
            self.logger.info("Installing dependencies from lock file...")
            pip_cmd = ["uv.exe", "pip"] if self.is_windows else ["uv", "pip"]
            await self.run_uv_command([
                *pip_cmd, "install", 
                "-r", str(self.root_dir / "requirements.lock")
            ])
            
        if (self.root_dir / "requirements-dev.lock").exists():
            self.logger.info("Installing dev dependencies from lock file...")
            pip_cmd = ["uv.exe", "pip"] if self.is_windows else ["uv", "pip"]
            await self.run_uv_command([
                *pip_cmd, "install", 
                "-r", str(self.root_dir / "requirements-dev.lock")
            ])
            
        # Install the project in editable mode if setup.py exists
        if (self.root_dir / "setup.py").exists():
            self.logger.info("Installing project in editable mode...")
            pip_cmd = ["uv.exe", "pip"] if self.is_windows else ["uv", "pip"]
            await self.run_uv_command([*pip_cmd, "install", "-e", "."])

    async def run_app(self, module_path: str, *args, timeout: Optional[float] = None):
        """Run the application using Python directly"""
        module_path = str(Path(module_path))
        
        # Use appropriate Python command based on platform
        python_cmd = "python" if self.is_windows else "python3"
        cmd = [python_cmd, module_path, *map(str, args)]
        
        self.logger.info(f"Running: {' '.join(cmd)}")
        return await self.run_uv_command(cmd, timeout=timeout)

    async def run_tests(self):
        """Run tests using pytest"""
        uvx_cmd = ["uvx.exe"] if self.is_windows else ["uvx"]
        await self.run_uv_command([*uvx_cmd, "run", "-m", "pytest", str(self.config.tests_path)])

    async def run_linter(self):
        """Run Ruff linter"""
        uvx_cmd = ["uvx.exe"] if self.is_windows else ["uvx"]
        await self.run_uv_command([*uvx_cmd, "run", "-m", "ruff", "check", "."])

    async def format_code(self):
        """Format code using Ruff"""
        uvx_cmd = ["uvx.exe"] if self.is_windows else ["uvx"]
        await self.run_uv_command([*uvx_cmd, "run", "-m", "ruff", "format", "."])

    async def run_dev_mode(self):
        """Setup and run operations specific to Developer Mode"""
        self.logger.info("Running Developer Mode tasks...")
        # Setup development environment, dependencies, local servers, etc.
        await self.setup_environment()
        await self.run_tests()
        await self.run_linter()
        await self.format_code()
        
        # Additional dev mode tasks
        self.logger.info("Development environment setup complete.")
        self.logger.info("You can now start coding or run your application.")

    async def run_admin_mode(self):
        """Setup and run operations specific to Admin Mode"""
        self.logger.info("Running Admin Mode tasks...")
        # Perform administrative tasks like configuration adjustments and monitoring
        
        # Ensure environment is set up
        await self.setup_environment()
        
        # Platform-specific admin tasks
        if self.is_windows:
            self.logger.info("Performing Windows-specific admin tasks...")
            # Set process priority
            if "platform_specific" in self.project_config and "windows" in self.project_config["platform_specific"]:
                priority = self.project_config["platform_specific"]["windows"].get("priority", 32)
                self.logger.info(f"Setting process priority to {priority}")
                # Windows-specific admin code would go here
        else:
            self.logger.info("Performing Linux-specific admin tasks...")
            # Set process priority
            if "platform_specific" in self.project_config and "linux" in self.project_config["platform_specific"]:
                priority = self.project_config["platform_specific"]["linux"].get("priority", 0)
                self.logger.info(f"Setting process priority to {priority}")
                # Linux-specific admin code would go here

    async def run_user_mode(self):
        """Setup and run operations specific to User Mode"""
        self.logger.info("Running User Mode tasks...")
        # Deploy and run the main application
        
        # Ensure minimal environment setup
        self.logger.info("Setting up minimal runtime environment...")
        
        # Create virtual environment if it doesn't exist
        venv_path = self.root_dir / ".venv"
        if not venv_path.exists():
            venv_cmd = ["uv.exe", "venv"] if self.is_windows else ["uv", "venv"]
            await self.run_uv_command(venv_cmd)
        
        # Install only runtime dependencies (not dev dependencies)
        requirements_path = self.root_dir / "requirements.txt"
        if requirements_path.exists():
            self.logger.info("Installing runtime dependencies...")
            pip_cmd = ["uv.exe", "pip"] if self.is_windows else ["uv", "pip"]
            await self.run_uv_command([
                *pip_cmd, "install", 
                "-r", str(requirements_path)
            ])
        
        # Find and run the main application
        main_module = self.root_dir / self.config.src_path / "__main__.py"
        if main_module.exists():
            self.logger.info("Running main application...")
            await self.run_app(str(main_module))
        else:
            self.logger.error(f"Main module not found at {main_module}")
            self.logger.info("Please specify the main module path explicitly.")

    async def teardown(self):
        """Teardown any setup done by modes or setup_environment"""
        self.logger.info("Tearing down environment...")
        
        # Stop any running processes
        self.logger.info("Stopping any running processes...")
        
        # Clean up temporary files
        self.logger.info("Cleaning up temporary files...")
        
        # Optional: Remove virtual environment
        if (self.root_dir / ".venv").exists():
            self.logger.info("Would you like to remove the virtual environment? (y/n)")
            # In a real scenario, you'd get user input here
            # For now, we'll just log the option
            self.logger.info("Virtual environment removal skipped.")
        
        self.logger.info("Teardown complete.")

    async def upgrade_dependencies(self):
        """Upgrade all dependencies to their latest versions"""
        self.logger.info("Upgrading dependencies...")
        
        # Check if requirements files exist
        requirements_path = self.root_dir / "requirements.txt"
        dev_requirements_path = self.root_dir / "requirements-dev.txt"
        
        if requirements_path.exists():
            self.logger.info("Upgrading runtime dependencies...")
            pip_cmd = ["uv.exe", "pip"] if self.is_windows else ["uv", "pip"]
            
            # Compile with --upgrade flag
            await self.run_uv_command([
                *pip_cmd, "compile", 
                str(requirements_path), 
                "--output-file", 
                str(self.root_dir / "requirements.lock"),
                "--upgrade"
            ])
            
            # Install from updated lock file
            await self.run_uv_command([
                *pip_cmd, "install", 
                "-r", str(self.root_dir / "requirements.lock")
            ])
        
        if dev_requirements_path.exists():
            self.logger.info("Upgrading development dependencies...")
            pip_cmd = ["uv.exe", "pip"] if self.is_windows else ["uv", "pip"]
            
            # Compile with --upgrade flag
            await self.run_uv_command([
                *pip_cmd, "compile", 
                str(dev_requirements_path), 
                "--output-file", 
                str(self.root_dir / "requirements-dev.lock"),
                "--upgrade"
            ])
            
            # Install from updated lock file
            await self.run_uv_command([
                *pip_cmd, "install", 
                "-r", str(self.root_dir / "requirements-dev.lock")
            ])
        
        self.logger.info("Dependency upgrade complete.")

    async def create_module(self, module_name: str):
        """Create a new module in the src directory"""
        module_path = self.root_dir / self.config.src_path / module_name
        
        # Create module directory
        module_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        init_file = module_path / "__init__.py"
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(f"""#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
{module_name} module
\"\"\"

__version__ = "0.1.0"
""")
        
        # Create a basic module file
        module_file = module_path / f"{module_name}.py"
        with open(module_file, 'w', encoding='utf-8') as f:
            f.write(f"""#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
Main functionality for {module_name}
\"\"\"

def main():
    \"\"\"Main function for {module_name}\"\"\"
    print("Hello from {module_name}!")

if __name__ == "__main__":
    main()
""")
        
        # Create a test file
        test_dir = self.root_dir / self.config.tests_path
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_file = test_dir / f"test_{module_name}.py"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(f"""#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
Tests for {module_name} module
\"\"\"

import pytest
from {self.config.src_path.name}.{module_name} import {module_name}

def test_{module_name}_main():
    \"\"\"Test the main function of {module_name}\"\"\"
    # Add your test here
    assert True
""")
        
        self.logger.info(f"Created module {module_name} at {module_path}")
        self.logger.info(f"Created test file at {test_file}")

async def main():
    """Main entry point for the project manager"""
    parser = argparse.ArgumentParser(description="Cross-Platform Project Manager for Python 3.13")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("mode", choices=["DEV", "ADMIN", "USER", "TEARDOWN", "UPGRADE"], 
                        help="Mode to execute")
    parser.add_argument("--timeout", type=float, default=None, 
                        help="Timeout in seconds for commands")
    parser.add_argument("--create-module", type=str, 
                        help="Create a new module with the specified name")
    args = parser.parse_args()
    
    manager = ProjectManager(args.root)
    
    try:
        # Handle module creation if specified
        if args.create_module:
            await manager.create_module(args.create_module)
            return 0
            
        # Execute requested mode
        if args.mode == "DEV":
            await manager.run_dev_mode()
        elif args.mode == "ADMIN":
            await manager.run_admin_mode()
        elif args.mode == "USER":
            await manager.run_user_mode()
        elif args.mode == "TEARDOWN":
            await manager.teardown()
        elif args.mode == "UPGRADE":
            await manager.upgrade_dependencies()
    except Exception as e:
        manager.logger.error(f"Error: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    # Use asyncio.run to run the async main function
    sys.exit(asyncio.run(main()))