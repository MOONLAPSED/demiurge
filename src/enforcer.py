#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import os
import sys
import io
import re
import dis
import ast
import tokenize
import importlib
import pathlib
import asyncio
import argparse
import uuid
import json
import struct
import time
import hashlib
import inspect
import threading
import logging
import shlex
import shutil
import subprocess
import ctypes
import tracemalloc
from enum import Enum, auto
from typing import (
    Any, Dict, List, Optional, Union, Callable, TypeVar, Tuple, Generic,
    Set, Coroutine, Type, NamedTuple
)
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from asyncio import Queue as AsyncQueue
from queue import Queue, Empty
from functools import wraps
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

class DotfileHandler:
    """Handles dotfile detection and filtering"""
    
    @staticmethod
    def is_dotfile(path: Path) -> bool:
        """
        Check if any part of the path is a dotfile (starts with a dot).
        This includes both files and directories.
        """
        return any(part.startswith('.') for part in path.parts)
    
    @staticmethod
    def should_ignore(path: Path, ignore_dotfiles: bool = True) -> bool:
        """
        Determine if a path should be ignored based on rules.
        """
        if ignore_dotfiles and DotfileHandler.is_dotfile(path):
            return True
        return False

class EnforcementLevel(Enum):
    ERROR = auto()
    WARNING = auto()
    INFO = auto()

@dataclass
class EnforcementResult:
    success: bool
    message: str
    level: EnforcementLevel
    name: str
    fixes_applied: bool = False
    details: Optional[Dict[str, Any]] = None

class EnforcementRule(abc.ABC):
    """Base class for all enforcement rules"""
    
    def __init__(self, name: str, level: EnforcementLevel = EnforcementLevel.ERROR):
        self.name = name
        self.level = level
    
    @abc.abstractmethod
    def check(self, context: Dict[str, Any]) -> EnforcementResult:
        """Check if the rule is satisfied"""
        pass
    
    @abc.abstractmethod
    def fix(self, context: Dict[str, Any]) -> EnforcementResult:
        """Apply fixes to satisfy the rule"""
        pass

class DirectoryStructureRule(EnforcementRule):
    """Enforces directory structure requirements"""
    
    def __init__(self, required_structure: Set[str], 
                 name: str = "Directory Structure",
                 level: EnforcementLevel = EnforcementLevel.ERROR):
        super().__init__(name, level)
        self.required_structure = required_structure
    
    def check(self, context: Dict[str, Any]) -> EnforcementResult:
        base_dir = context['base_dir']
        missing_dirs = []
        
        for root, _, _ in os.walk(base_dir):
            current_path = Path(root)
            if current_path.name in {'assets', 'pub'} or \
               any(part.startswith('.') for part in current_path.parts):
                continue
                
            for required_subdir in self.required_structure:
                subdir_path = current_path / required_subdir
                if not subdir_path.exists():
                    missing_dirs.append(str(subdir_path.relative_to(base_dir)))
        
        if missing_dirs:
            return EnforcementResult(
                success=False,
                message=f"Missing required directories: {', '.join(missing_dirs)}",
                level=self.level,
                name=self.name,
                details={'missing_dirs': missing_dirs}
            )
        return EnforcementResult(
            success=True, 
            message="Directory structure is correct", 
            level=self.level,
            name=self.name
        )

    def fix(self, context: Dict[str, Any]) -> EnforcementResult:
        base_dir = context['base_dir']
        created_dirs = []
        
        for root, _, _ in os.walk(base_dir):
            current_path = Path(root)
            if current_path.name in {'assets', 'pub'} or \
               any(part.startswith('.') for part in current_path.parts):
                continue
                
            for required_subdir in self.required_structure:
                subdir_path = current_path / required_subdir
                if not subdir_path.exists():
                    subdir_path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(str(subdir_path.relative_to(base_dir)))
        
        return EnforcementResult(
            success=True,
            message=f"Created directories: {', '.join(created_dirs)}" if created_dirs else "No directories needed creation",
            level=self.level,
            fixes_applied=bool(created_dirs),
            name=self.name,
            details={'created_dirs': created_dirs}
        )

class GitignoreRule(EnforcementRule):
    """Enforces .gitignore rules"""
    
    END_TOKEN = "### END AUTOMATED SECTION ###"
    
    def __init__(self, required_patterns: Dict[str, List[str]], 
                 name: str = "Gitignore Rules",
                 level: EnforcementLevel = EnforcementLevel.ERROR):
        super().__init__(name, level)
        self.required_patterns = required_patterns
    
    def _generate_rules(self) -> List[str]:
        rules = ["# Automated rules - DO NOT MODIFY", ""]
        
        for section, patterns in self.required_patterns.items():
            rules.extend([f"# {section}", ""])
            rules.extend(patterns)
            rules.append("")
        
        rules.append(self.END_TOKEN)
        return rules
    
    def check(self, context: Dict[str, Any]) -> EnforcementResult:
        gitignore_path = context['base_dir'] / '.gitignore'
        if not gitignore_path.exists():
            return EnforcementResult(
                success=False,
                message=".gitignore file is missing",
                level=self.level,
                name=self.name
            )
            
        current_content = gitignore_path.read_text()
        required_content = '\n'.join(self._generate_rules())
        
        if self.END_TOKEN not in current_content:
            return EnforcementResult(
                success=False,
                message=".gitignore is missing automated section",
                level=self.level,
                name=self.name
            )
            
        current_automated = current_content.split(self.END_TOKEN)[0]
        if current_automated.strip() != required_content.strip():
            return EnforcementResult(
                success=False,
                message=".gitignore automated rules need updating",
                level=self.level,
                name=self.name
            )
            
        return EnforcementResult(success=True, message=".gitignore rules are correct", level=self.level, name=self.name)
    
    def fix(self, context: Dict[str, Any]) -> EnforcementResult:
        gitignore_path = context['base_dir'] / '.gitignore'
        new_rules = self._generate_rules()
        
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            if self.END_TOKEN in content:
                user_content = content.split(self.END_TOKEN)[1]
            else:
                user_content = content
        else:
            user_content = "\n\n# User-defined rules below\n"
        
        new_content = '\n'.join(new_rules) + user_content
        gitignore_path.write_text(new_content)
        
        return EnforcementResult(
            success=True,
            message=".gitignore rules updated",
            level=self.level,
            fixes_applied=True,
            name=self.name
        )
class RuffRule(EnforcementRule):
    """Enforces Python code style using ruff"""
    
    def __init__(self, name: str = "Ruff Linting",
                 level: EnforcementLevel = EnforcementLevel.WARNING):
        super().__init__(name, level)
    
    def check(self, context: Dict[str, Any]) -> EnforcementResult:
        if not shutil.which('ruff'):
            return EnforcementResult(
                success=False,
                message="Ruff is not installed",
                level=self.level,
                name=self.name
            )
        
        try:
            result = subprocess.run(
                ['ruff', 'check', str(context['base_dir'])],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                return EnforcementResult(
                    success=False,
                    message="Ruff found issues",
                    level=self.level,
                    details={'output': result.stdout},
                    name=self.name
                )
            return EnforcementResult(success=True, message="Ruff check passed", level=self.level, name=self.name)
        except Exception as e:
            return EnforcementResult(
                success=False,
                message=f"Ruff check failed: {str(e)}",
                level=self.level,
                name=self.name
            )
    
    def fix(self, context: Dict[str, Any]) -> EnforcementResult:
        try:
            result = subprocess.run(
                ['ruff', 'check', '--fix', str(context['base_dir'])],
                capture_output=True,
                text=True
            )
            return EnforcementResult(
                success=result.returncode == 0,
                message="Ruff fixes applied" if result.returncode == 0 else "Ruff fix failed",
                level=self.level,
                fixes_applied=True,
                details={'output': result.stdout},
                name=self.name
            )
        except Exception as e:
            return EnforcementResult(
                success=False,
                message=f"Ruff fix failed: {str(e)}",
                level=self.level,
                name=self.name
            )
class ProjectEnforcer:
    """Main enforcer class that manages and runs all enforcement rules"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.rules: List[EnforcementRule] = []
        self.context = {'base_dir': base_dir}
    
    def add_rule(self, rule: EnforcementRule):
        """Add an enforcement rule"""
        self.rules.append(rule)
    
    def check_all(self, fix: bool = False) -> List[EnforcementResult]:
        """Check all rules and optionally apply fixes"""
        results = []
        
        for rule in self.rules:
            check_result = rule.check(self.context)
            if not check_result.success and fix:
                fix_result = rule.fix(self.context)
                results.append(fix_result)
            else:
                results.append(check_result)
        
        return results

def load_config(config_path: Path) -> Dict[str, Any]:
    """Load enforcer configuration from JSON file"""
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path) as f:
            return json.load(f)
    except ImportError as e:
        print(f"Error parsing config file: {e}", file=sys.stderr)
        print(f"Error location: line {e.lineno}, column {e.colno}", file=sys.stderr)
        sys.exit(1)

def create_enforcer(config: Dict[str, Any], base_dir: Path) -> ProjectEnforcer:
    """Create and configure an enforcer instance based on config"""
    enforcer = ProjectEnforcer(base_dir)
    
    # Add directory structure rule if enabled
    dir_config = config.get('directory_structure', {})
    if dir_config.get('enabled', False):
        enforcer.add_rule(DirectoryStructureRule(
            required_structure=set(dir_config.get('paths', [])),
            level=EnforcementLevel[dir_config.get('level', 'ERROR')]
        ))
    
    # Add gitignore rule if enabled
    git_config = config.get('gitignore', {})
    if git_config.get('enabled', False):
        enforcer.add_rule(GitignoreRule(
            required_patterns=git_config.get('patterns', {}),
            level=EnforcementLevel[git_config.get('level', 'ERROR')]
        ))
    
    # Add ruff rule if enabled
    ruff_config = config.get('ruff', {})
    if ruff_config.get('enabled', False):
        enforcer.add_rule(RuffRule(
            level=EnforcementLevel[ruff_config.get('level', 'WARNING')]
        ))
    
    # Add custom rules
    for name, rule_config in config.get('custom_rules', {}).items():
        if rule_config.get('enabled', False):
            enforcer.add_rule(CustomCommandRule(
                name=name,
                check_command=rule_config['check_command'],
                fix_command=rule_config.get('fix_command'),
                success_exit_codes=set(rule_config.get('success_exit_codes', [0])),
                level=EnforcementLevel[rule_config.get('level', 'WARNING')]
            ))
    
    return enforcer

def create_default_config(path: Path):
    """Create a default configuration file with comments"""
    default_config = {
        "base_dir": ".",
        "directory_structure": {
            "enabled": True,
            "level": "ERROR",
            "paths": [
                "assets/pub",
                "kb/assets/pub",
                "kb/pub"
            ]
        },
        "gitignore": {
            "enabled": True,
            "level": "ERROR",
            "patterns": {
                "private": [
                    "/assets/*",
                    "/kb/*",
                    "/kb/assets/*"
                ],
                "public": [
                    "!/assets/pub/",
                    "!/kb/pub/",
                    "!/kb/assets/pub/*"
                ]
            }
        },
        "ruff": {
            "enabled": False,
            "level": "WARNING"
        },
        "hooks": {
            "enabled": False,
            "pre_commit": [
                "enforcer.py --check"
            ],
            "pre_push": [
                "enforcer.py --check"
            ]
        },
        "custom_rules": {
            "example_rule": {
                "enabled": False,
                "level": "WARNING",
                "check_command": "mypy .",
                "fix_command": "black .",
                "success_exit_codes": [0]
            }
        }
    }
    
    with open(path, 'w') as f:
        json.dump(default_config, f, indent=2)
        f.write('\n')

class CustomCommandRule(EnforcementRule):
    """Rule for running custom commands"""
    
    def __init__(self, name: str, check_command: str, fix_command: Optional[str] = None,
                 success_exit_codes: Set[int] = {0},
                 level: EnforcementLevel = EnforcementLevel.WARNING):
        super().__init__(name, level)
        self.check_command = check_command
        self.fix_command = fix_command
        self.success_exit_codes = success_exit_codes
    
    def _run_command(self, command: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            command.split(),
            capture_output=True,
            text=True
        )
    
    def check(self, context: Dict[str, Any]) -> EnforcementResult:
        try:
            result = self._run_command(self.check_command)
            success = result.returncode in self.success_exit_codes
            return EnforcementResult(
                success=success,
                message=f"Command '{self.check_command}' " + 
                       ("succeeded" if success else "failed"),
                level=self.level,
                details={'output': result.stdout, 'error': result.stderr},
                name=self.name
            )
        except Exception as e:
            return EnforcementResult(
                success=False,
                message=f"Command failed: {str(e)}",
                level=self.level,
                name=self.name
            )
    
    def fix(self, context: Dict[str, Any]) -> EnforcementResult:
        if not self.fix_command:
            return EnforcementResult(
                success=False,
                message="No fix command specified",
                level=self.level,
                name=self.name
            )
        
        try:
            result = self._run_command(self.fix_command)
            success = result.returncode in self.success_exit_codes
            return EnforcementResult(
                success=success,
                message=f"Fix command '{self.fix_command}' " +
                       ("succeeded" if success else "failed"),
                level=self.level,
                fixes_applied=True,
                details={'output': result.stdout, 'error': result.stderr},
                name=self.name
            )
        except Exception as e:
            return EnforcementResult(
                success=False,
                message=f"Fix command failed: {str(e)}",
                level=self.level,
                name=self.name
            )

def setup_git_hooks(config: Dict[str, Any], base_dir: Path):
    """Set up git hooks based on configuration"""
    if not config.get('hooks', {}).get('enabled', False):
        return
    
    hooks_dir = base_dir / '.git' / 'hooks'
    if not hooks_dir.exists():
        return
    
    hook_template = '''#!/bin/sh
# Generated by enforcer.py
{commands}
'''
    
    hooks_config = config['hooks']
    for hook_name, commands in hooks_config.items():
        if hook_name == 'enabled':
            continue
            
        hook_path = hooks_dir / hook_name
        with open(hook_path, 'w') as f:
            f.write(hook_template.format(
                commands='\n'.join(commands)
            ))
        hook_path.chmod(0o755)  # Make executable

def main():
    parser = argparse.ArgumentParser(description='Project Structure Enforcer')
    parser.add_argument('--check', action='store_true',
                       help='Check rules without applying fixes')
    parser.add_argument('--config', type=Path, default=Path('enforcer.json'),
                       help='Path to config file')
    parser.add_argument('--init', action='store_true',
                       help='Create a default config file')
    args = parser.parse_args()
    
    try:
        if args.init:
            create_default_config(args.config)
            print(f"Created default config file at {args.config}")
            return
        
        config = load_config(args.config)
        base_dir = Path(config.get('base_dir', '.')).resolve()
        
        # Set up git hooks if configured
        setup_git_hooks(config, base_dir)
        
        enforcer = create_enforcer(config, base_dir)
        results = enforcer.check_all(fix=not args.check)
        
        exit_code = 0
        for result in results:
            if not result.success and result.level == EnforcementLevel.ERROR:
                exit_code = 1
            
            status = "✓" if result.success else "✗"
            print(f"{status} {result.name}: {result.message}")
            
            if not result.success and result.details:
                for key, value in result.details.items():
                    if key in ['output', 'error'] and value.strip():
                        print(f"  {key}:")
                        for line in value.strip().split('\n'):
                            print(f"    {line}")
                    elif value:
                        print(f"  {key}: {value}")
        
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()