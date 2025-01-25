import os
import tracemalloc
import logging
import threading
import gc
import weakref
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Set, TypeVar, Union
from contextlib import contextmanager
from functools import wraps
from dataclasses import dataclass
from enum import Enum, auto

# Type variables for generic type hints
T = TypeVar('T')

class MemoryTraceLevel(Enum):
    """Granularity levels for memory tracing."""
    BASIC = auto()      # Basic memory usage
    DETAILED = auto()   # Include stack traces
    FULL = auto()       # Include object references

@dataclass
class MemoryStats:
    """Container for memory statistics with analysis capabilities."""
    size: int
    count: int
    traceback: str
    timestamp: float
    peak_memory: int
    
    def to_dict(self) -> Dict:
        return {
            'size': self.size,
            'count': self.count,
            'traceback': self.traceback,
            'timestamp': self.timestamp,
            'peak_memory': self.peak_memory
        }

class CustomFormatter(logging.Formatter):
    """Custom formatter for color-coded log levels."""
    COLORS = {
        logging.DEBUG: "\x1b[38;20m",
        logging.INFO: "\x1b[32;20m",
        logging.WARNING: "\x1b[33;20m",
        logging.ERROR: "\x1b[31;20m",
        logging.CRITICAL: "\x1b[31;1m"
    }
    RESET = "\x1b[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.COLORS[logging.DEBUG])
        record.msg = f"{color}{record.msg}{self.RESET}"
        return super().format(record)

class MemoryTracker:
    """Singleton memory tracking manager with enhanced logging."""
    _instance = None
    _lock = threading.Lock()
    _trace_filter = {"<frozen importlib._bootstrap>", "<frozen importlib._bootstrap_external>"}
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        """Initialize the memory tracker with logging and storage."""
        self._setup_logging()
        self._snapshots: Dict[str, List[MemoryStats]] = {}
        self._tracked_objects = weakref.WeakSet()
        self._trace_level = MemoryTraceLevel.DETAILED
        
        # Start tracemalloc if not already running
        if not tracemalloc.is_tracing():
            tracemalloc.start()
    
    def _setup_logging(self):
        """Configure logging with custom formatter."""
        self.logger = logging.getLogger("MemoryTracker")
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler with color formatting
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(CustomFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))
        self.logger.addHandler(console_handler)
        
        # File handler for persistent logging
        try:
            file_handler = logging.FileHandler("memory_tracker.log")
            file_handler.setFormatter(logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ))
            self.logger.addHandler(file_handler)
        except (PermissionError, IOError) as e:
            self.logger.warning(f"Could not create log file: {e}")

def trace_memory(level: MemoryTraceLevel = MemoryTraceLevel.DETAILED):
    """Enhanced decorator for memory tracking with configurable detail level."""
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            tracker = MemoryTracker()
            
            # Force garbage collection for accurate measurement
            gc.collect()
            
            # Take initial snapshot
            snapshot_before = tracemalloc.take_snapshot()
            
            try:
                result = method(self, *args, **kwargs)
                
                # Take final snapshot and compute statistics
                snapshot_after = tracemalloc.take_snapshot()
                stats = snapshot_after.compare_to(snapshot_before, 'lineno')
                
                # Filter and process statistics
                filtered_stats = [
                    stat for stat in stats 
                    if not any(f in str(stat.traceback) for f in tracker._trace_filter)
                ]
                
                # Log based on trace level
                if level in (MemoryTraceLevel.DETAILED, MemoryTraceLevel.FULL):
                    for stat in filtered_stats[:5]:
                        tracker.logger.info(
                            f"Memory change in {method.__name__}: "
                            f"+{stat.size_diff/1024:.1f} KB at:\n{stat.traceback}"
                        )
                
                return result
                
            finally:
                # Cleanup
                del snapshot_before
                gc.collect()
                
        return wrapper
    return decorator

class MemoryTrackedABC(ABC):
    """Abstract base class for memory-tracked classes with enhanced features."""
    
    def __init__(self):
        self._tracker = MemoryTracker()
        self._tracker._tracked_objects.add(self)
    
    def __init_subclass__(cls):
        super().__init_subclass__()
        
        # Store original methods for introspection
        cls._original_methods = {}
        
        # Automatically decorate public methods
        for attr_name, attr_value in cls.__dict__.items():
            if (callable(attr_value) and 
                not attr_name.startswith('_') and 
                not getattr(attr_value, '_skip_trace', False)):
                cls._original_methods[attr_name] = attr_value
                setattr(cls, attr_name, trace_memory()(attr_value))
    
    @staticmethod
    def skip_trace(method: Callable) -> Callable:
        """Decorator to exclude a method from memory tracking."""
        method._skip_trace = True
        return method
    
    @classmethod
    @contextmanager
    def trace_section(cls, section_name: str, level: MemoryTraceLevel = MemoryTraceLevel.DETAILED):
        """Context manager for tracking memory usage in specific code sections."""
        tracker = MemoryTracker()
        
        gc.collect()
        snapshot_before = tracemalloc.take_snapshot()
        
        try:
            yield
        finally:
            snapshot_after = tracemalloc.take_snapshot()
            stats = snapshot_after.compare_to(snapshot_before, 'lineno')
            
            filtered_stats = [
                stat for stat in stats 
                if not any(f in str(stat.traceback) for f in tracker._trace_filter)
            ]
            
            if level != MemoryTraceLevel.BASIC:
                tracker.logger.info(f"\nMemory usage for section '{section_name}':")
                for stat in filtered_stats[:5]:
                    tracker.logger.info(f"{stat}")
            
            del snapshot_before
            gc.collect()








class DebuggerMixin:
    """Mixin for debugging memory-tracked classes."""

    def __init__(self):
        self._tracker = MemoryTracker()
        self._tracker._tracked_objects.add(self)

    def __init_subclass__(cls):
        super().__init_subclass__()

        # Store original methods for introspection
        cls._original_methods = {}

        # Automatically decorate public methods
        for attr_name, attr_value in cls.__dict__.items():
            if (callable(attr_value) and
                not attr_name.startswith('_') and
                not getattr(attr_value, '_skip_trace', False)):
                cls._original_methods[attr_name] = attr_value
                setattr(cls, attr_name, trace_memory()(attr_value))

    @staticmethod
    def skip_trace(method: Callable) -> Callable:
        """Decorator to exclude a method from memory tracking."""
        method._skip_trace = True
        return method

    @classmethod
    @contextmanager
    def trace_section(cls, section_name: str, level: MemoryTraceLevel = MemoryTraceLevel.DETAILED):
        """Context manager for tracking memory usage in specific code sections."""
        tracker = MemoryTracker()

def main():
    class MyTrackedClass(MemoryTrackedABC):
        def tracked_method(self):
            """This method will be automatically tracked with detailed memory info."""
            large_list = [i for i in range(1000000)]
            return sum(large_list)
        
        @MemoryTrackedABC.skip_trace
        def untracked_method(self):
            """This method will not be tracked."""
            return "Not tracked"
        
        def tracked_with_section(self):
            """Example of using trace_section with different detail levels."""
            with self.trace_section("initialization", MemoryTraceLevel.BASIC):
                result = []
                
            with self.trace_section("processing", MemoryTraceLevel.DETAILED):
                result.extend(i * 2 for i in range(500000))
                
            with self.trace_section("cleanup", MemoryTraceLevel.FULL):
                result.clear()
                
            return len(result)
    
        @classmethod
        def introspect_methods(cls):
            """Introspect and display tracked methods with their original implementations."""
            for method_name, original_method in cls._original_methods.items():
                print(f"Method: {method_name}")
                print(f"Original implementation: {original_method}")
                print("---")

            return MyTrackedClass()
    return MyTrackedClass()

if __name__ == "__main__":
    tracker = MemoryTracker()
    tracker.logger.setLevel(logging.DEBUG)
    tracker.logger.addHandler(logging.StreamHandler())
    tracker.logger.addHandler(logging.FileHandler("memory_tracker.log"))
    my_instance = main()
    my_instance.__class__.introspect_methods()

    MyTrackedClass = main().__class__
    MyTrackedClass.introspect_methods()


    # Basic usage
    obj = MyTrackedClass()
    obj.tracked_method()  # Automatically tracked with detailed info

    # Custom section tracking with different detail levels
    obj.tracked_with_section()

    # Customize tracking level for specific methods
    @trace_memory(level=MemoryTraceLevel.FULL)
    def custom_tracked_method(self):
        pass