import os
import asyncio
import math
import random
import weakref
from typing import List, Set, Dict, Union, Callable, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import uuid
import time
import subprocess
from pathlib import Path
from enum import Enum, StrEnum
from contextlib import asynccontextmanager

class QuantumState(Enum):
    SUPERPOSITION = "SUPERPOSITION"  # Initial state
    ENTANGLED = "ENTANGLED"         # Linked to other instances
    COLLAPSED = "COLLAPSED"         # Materialized state
    DECOHERENT = "DECOHERENT"      # Failed/garbage collected

@dataclass
class RuntimeMetadata:
    canonical_time: float
    instance_id: str
    git_commit: str
    git_branch: str
    filesystem_state: Dict[str, Any]

class QuinicRuntime:
    """A self-aware runtime that can observe and modify its own state"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.state = QuantumState.SUPERPOSITION
        self.metadata = self._initialize_metadata()
        self.statistics = StatisticalDynamics(self)
        self.consensus = LazyConsensus(self)
        
    def _initialize_metadata(self) -> RuntimeMetadata:
        """Create initial runtime metadata including git and filesystem state"""
        return RuntimeMetadata(
            canonical_time=time.time_ns() / 1e9,  # High precision timestamp
            instance_id=str(uuid.uuid4()),
            git_commit=self._get_git_commit(),
            git_branch=self._get_git_branch(),
            filesystem_state=self._get_fs_state()
        )
    
    async def create_quantum_branch(self, name: str) -> None:
        """Create a new quantum superposition branch"""
        await self.statistics._run_git(['checkout', '-b', name])
        await self.statistics.evolve_state()
        
    async def collapse_to_consensus(self) -> bool:
        """Collapse quantum states to consensus state"""
        consensus_commit = await self.consensus.seek_consensus()
        if consensus_commit:
            # Move to consensus state
            await self.statistics._run_git(['checkout', consensus_commit])
            self.state = QuantumState.COLLAPSED
            return True
        return False

    @asynccontextmanager
    async def quantum_computation(self):
        """Enhanced quantum context with statistical dynamics"""
        branch_name = f'quantum-{uuid.uuid4().hex[:8]}'
        try:
            await self.create_quantum_branch(branch_name)
            self.state = QuantumState.ENTANGLED
            yield self
            # Try to reach consensus
            if await self.collapse_to_consensus():
                self.state = QuantumState.COLLAPSED
            else:
                self.state = QuantumState.DECOHERENT
        except Exception:
            self.state = QuantumState.DECOHERENT
            raise
        finally:
            # Cleanup temporary quantum branch
            try:
                await self.statistics._run_git(['branch', '-D', branch_name])
            except subprocess.CalledProcessError:
                pass

    @asynccontextmanager
    async def quantum_context(self):
        """Context manager for quantum state transitions"""
        try:
            self.state = QuantumState.ENTANGLED
            yield self
            self.state = QuantumState.COLLAPSED
        except Exception:
            self.state = QuantumState.DECOHERENT
            raise

    def _get_git_commit(self) -> str:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.base_path,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except subprocess.SubprocessError:
            return "unknown"
            
    def _get_git_branch(self) -> str:
        """Get current git branch name"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.base_path,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except subprocess.SubprocessError:
            return "unknown"

    def _snapshot_fs_state(self) -> Dict[str, Any]:
        """Capture filesystem state for this runtime instance"""
        state = {}
        try:
            result = subprocess.run(
                ['git', 'ls-files', '-s'],
                cwd=self.base_path,
                capture_output=True,
                text=True
            )
            for line in result.stdout.splitlines():
                mode, _, hash_, path = line.split(None, 3)
                state[path] = {'mode': mode, 'hash': hash_}
        except subprocess.CalledProcessError:
            raise RuntimeError("Failed to snapshot filesystem state")

        try:        
            for root, dirs, files in os.walk(self.base_path):
                rel_path = Path(root).relative_to(self.base_path)
                state[str(rel_path)] = {
                    'dirs': dirs,
                    'files': files,
                    'permissions': os.stat(root).st_mode
                }
            return state
        except:
            raise RuntimeError("Failed to snapshot filesystem state")

    def _get_fs_state(self) -> Dict[str, Any]:
        """Capture filesystem state for this runtime instance"""
        state = {}
        for root, dirs, files in os.walk(self.base_path):
            rel_path = Path(root).relative_to(self.base_path)
            state[str(rel_path)] = {
                'dirs': dirs,
                'files': files,
                'permissions': os.stat(root).st_mode
            }
        return state

    def validate_instance(self) -> bool:
        """Validate runtime instance integrity"""
        try:
            # Check filesystem permissions
            if not os.access(self.base_path, os.R_OK | os.W_OK | os.X_OK):
                print("Filesystem permissions are invalid.")
                return False
            
            # Validate git state
            current_commit = self._get_git_commit()
            if current_commit != self.metadata.git_commit:
                print(f"Git commit mismatch: {current_commit} != {self.metadata.git_commit}")
                return False
            
            # Validate git repository state
            if subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.base_path,
                capture_output=True
            ).returncode != 0:
                print("Invalid git repository state.")
                return False

            # Validate filesystem state
            current_fs_state = self._snapshot_fs_state()
            expected_fs_state = self.metadata.filesystem_state
            if current_fs_state != expected_fs_state:
                print("Filesystem state mismatch.")
                print(f"Current FS State: {current_fs_state}")
                print(f"Expected FS State: {expected_fs_state}")
                return False
            
            return True
        except Exception as e:
            print(f"Validation error: {e}")
            self.state = QuantumState.DECOHERENT
            return False

    def quine(self) -> Optional['QuinicRuntime']:
        """Create a new runtime instance with genetic inheritance"""
        """Create a new runtime instance maintaining quantum entanglement"""
        if self.state == QuantumState.DECOHERENT:
            raise RuntimeError("Cannot quine from decoherent state")
            
        # Create new instance with shared git history
        new_instance = QuinicRuntime(self.base_path)
        
        # Establish entanglement through git
        subprocess.run(
            ['git', 'notes', 'append', '-m', f'entangled:{self.metadata.instance_id}'],
            cwd=self.base_path
        )
        if not self.validate_instantiation():
            return None
            
        # Create new branch for this instance
        new_branch = f"quinic/{self.metadata.instance_id}"
        subprocess.run(
            ["git", "checkout", "-b", new_branch],
            cwd=self.base_path
        )
        
        # Initialize new runtime with inherited state
        new_runtime = QuinicRuntime(self.base_path)
        new_runtime.state = QuantumState.ENTANGLED
        
        return new_runtime

    async def run_quantum_computation(self, computation):
        """Execute computation maintaining quantum state awareness"""
        async with self.quantum_context():
            if not self.validate_instance():
                raise RuntimeError("Invalid runtime state")
                
            try:
                result = await computation(self)
                
                # Record computation in git
                subprocess.run([ 
                    'git', 'commit', '-m',
                    f'compute:{self.metadata.instance_id}\n\n{result}'
                ], cwd=self.base_path)
                
                return result
            except Exception as e:
                self.state = QuantumState.DECOHERENT
                raise RuntimeError(f"Computation failed: {e}")

    def commit_state(self, message: str) -> bool:
        """Commit current state to git"""
        try:
            # Stage all changes
            subprocess.run(
                ["git", "add", "."],
                cwd=self.base_path,
                check=True
            )
            
            # Create commit with metadata
            commit_msg = f"""
            Quinic State Transition
            
            Instance: {self.metadata.instance_id}
            Time: {self.metadata.canonical_time}
            State: {self.state.value}
            
            {message}
            """
            
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.base_path,
                check=True
            )
            
            # Update metadata
            self.metadata.git_commit = self._get_git_commit()
            return True
            
        except subprocess.SubprocessError:
            return False

    def __enter__(self):
        """Enable context manager pattern for state management"""
        return self.quantum_context().__enter__()
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup when exiting context"""
        return self.quantum_context().__exit__(exc_type, exc_val, exc_tb)

def create_quinic_runtime(path: Optional[Path] = None) -> QuinicRuntime:
    """Factory function to create a new quinic runtime instance"""
    if path is None:
        path = Path.cwd()
    return QuinicRuntime(path)

@dataclass
class BranchState:
    """Represents a quantum superposition in git branch space"""
    name: str
    commit_hash: str
    superposition_factor: float  # Probability amplitude
    entangled_branches: Set[str]

class StatisticalDynamics:
    """Handles statistical evolution of quantum states across git branches"""
    def __init__(self, runtime: 'QuinicRuntime'):
        self.runtime = runtime
        self.branch_states: Dict[str, BranchState] = {}
        self.coherence_threshold = 0.1  # Minimum probability to maintain branch
        
    async def evolve_state(self) -> None:
        """Evolve quantum states across all branches"""
        # Get current branch states
        branches = await self._get_branch_states()
        
        # Calculate superposition factors
        total_weight = sum(1.0 for _ in branches)
        for branch in branches:
            state = BranchState(
                name=branch,
                commit_hash=await self._get_branch_head(branch),
                superposition_factor=1.0/total_weight,
                entangled_branches=set()
            )
            self.branch_states[branch] = state
            
        # Identify and record entanglements
        await self._detect_entanglements()
        
        # Prune decoherent branches
        await self._prune_decoherent_states()

    async def _get_branch_states(self) -> List[str]:
        """Get all git branches"""
        result = await self._run_git(['branch', '--list', '--format=%(refname:short)'])
        return result.splitlines()

    async def _get_branch_head(self, branch: str) -> str:
        """Get HEAD commit hash for branch"""
        result = await self._run_git(['rev-parse', branch])
        return result.strip()

    async def _detect_entanglements(self) -> None:
        """Detect entangled branches through common ancestry"""
        for branch1 in self.branch_states:
            for branch2 in self.branch_states:
                if branch1 != branch2:
                    # Find merge-base (common ancestor)
                    try:
                        merge_base = await self._run_git(
                            ['merge-base', branch1, branch2]
                        )
                        if merge_base.strip():
                            # Branches are entangled through common history
                            self.branch_states[branch1].entangled_branches.add(branch2)
                            self.branch_states[branch2].entangled_branches.add(branch1)
                    except subprocess.CalledProcessError:
                        continue

    async def _prune_decoherent_states(self) -> None:
        """Remove branches that have decohered below threshold"""
        decoherent = [
            branch for branch, state in self.branch_states.items()
            if state.superposition_factor < self.coherence_threshold
        ]
        for branch in decoherent:
            await self._run_git(['branch', '-D', branch])
            del self.branch_states[branch]

    async def _run_git(self, args: List[str]) -> str:
        """Run git command asynchronously"""
        proc = await asyncio.create_subprocess_exec(
            'git', *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.runtime.base_path
        )
        stdout, _ = await proc.communicate()
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, args)
        return stdout.decode().strip()

class LazyConsensus:
    """Implements lazy consensus through git branch evolution"""
    def __init__(self, runtime: 'QuinicRuntime'):
        self.runtime = runtime
        self.statistics = StatisticalDynamics(runtime)
        self.consensus_threshold = 0.7  # Minimum agreement for consensus
        
    async def seek_consensus(self) -> Optional[str]:
        """
        Attempt to reach consensus across quantum branches.
        Returns consensus branch name if found.
        """
        await self.statistics.evolve_state()
        
        # Calculate branch weights
        branch_weights = defaultdict(float)
        for state in self.statistics.branch_states.values():
            branch_weights[state.commit_hash] += state.superposition_factor
            
        # Find highest weight commit
        if branch_weights:
            consensus_commit, weight = max(
                branch_weights.items(), 
                key=lambda x: x[1]
            )
            if weight >= self.consensus_threshold:
                return consensus_commit
        return None


async def create_statistical_runtime(path: Optional[Path] = None) -> QuinicRuntime:
    """Create runtime with statistical dynamics enabled"""
    if path is None:
        path = Path.cwd()
    runtime = QuinicRuntime(path)
    await runtime.statistics.evolve_state()
    return runtime

@dataclass
class QuantumFrame:
    """
    Represents a cognitive frame in a quantum computation environment.
    Each frame is entangled with others and encodes a latent vector.
    """
    surface_form: str
    latent_vector: List[float]
    entangled_frames: Set[str] = None
    recursive_depth: int = 0

    def __post_init__(self):
        if self.entangled_frames is None:
            self.entangled_frames = set()

    def entangle(self, other: 'QuantumFrame') -> None:
        """
        Entangles this frame with another based on similarity or recursion patterns.
        """
        if self.should_entangle(other):
            self.entangled_frames.add(other.surface_form)
            other.entangled_frames.add(self.surface_form)

    def should_entangle(self, other: 'QuantumFrame') -> bool:
        """
        Determines if two frames should be entangled based on their latent vectors
        and recursive structures.
        """
        similarity = self.cosine_similarity(other.latent_vector)
        return similarity > 0.8

    def cosine_similarity(self, vec: List[float]) -> float:
        dot_product = sum(x * y for x, y in zip(self.latent_vector, vec))
        magnitude_self = math.sqrt(sum(x * x for x in self.latent_vector))
        magnitude_vec = math.sqrt(sum(y * y for y in vec))
        return dot_product / (magnitude_self * magnitude_vec) if magnitude_self and magnitude_vec else 0.0

# ===============================================================================

def main():
    # Synchronous entry point
    runtime = create_quinic_runtime(Path.cwd())
    print(f"Runtime created with ID: {runtime.metadata.instance_id}")
    
    # Example of validating the instance
    if runtime.validate_instance():
        print("Runtime instance is valid.")
    else:
        print("Runtime instance is invalid.")

async def asyncmain():
    # Asynchronous entry point
    runtime = await create_statistical_runtime(Path.cwd())
    print(f"Async Runtime created with ID: {runtime.metadata.instance_id}")
    
    # Example of running a quantum computation
    async def sample_computation(runtime):
        # Placeholder for a computation
        return "Sample computation result"

    try:
        result = await runtime.run_quantum_computation(sample_computation)
        print(f"Computation result: {result}")
    except RuntimeError as e:
        print(f"Error during computation: {e}")

if __name__ == "__main__":
    main()
    asyncio.run(asyncmain())
