from typing import TypeVar, Generic, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from functools import reduce
import hashlib
import subprocess
from datetime import datetime
import json
import os

T = TypeVar('T')
StateHash = str  # Type alias for state hashes

class StateType(Enum):
    QUANTUM = "quantum"  # Superposition of states
    CLASSICAL = "classical"  # Collapsed state
    ENTANGLED = "entangled"  # Linked states

@dataclass(frozen=True)
class GitCommitState:
    """Immutable representation of a git commit state"""
    commit_hash: str
    timestamp: datetime
    state_type: StateType
    parent_hashes: Tuple[str, ...]

class QuantumStateRing(Generic[T]):
    """
    Represents a quantum state ring backed by git commits.
    Each state transition is recorded as a commit, allowing
    for time-reversible computations.
    """
    def __init__(self):
        self.states: Dict[StateHash, T] = {}
        self.current_state: Optional[StateHash] = None
        self._commit_map: Dict[StateHash, GitCommitState] = {}

    def _make_commit(self, state: T, message: str) -> GitCommitState:
        """Create a git commit for the current state"""
        if not self._is_git_repo():
            raise RuntimeError("Not a valid Git repository")

        timestamp = datetime.now()
        state_hash = hashlib.sha256(str(state).encode()).hexdigest()

        # Save state to a file
        state_file = 'state.json'
        with open(state_file, 'w') as f:
            json.dump(state, f)

        # Create git commit
        try:
            subprocess.run(['git', 'add', state_file], check=True)
            subprocess.run(['git', 'commit', '-m', f"{message}: {state_hash[:8]}", '--allow-empty'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Git commit failed: {e}")
            raise

        # Get commit hash
        commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()

        # Get parent commits
        parent_cmd = ['git', 'rev-parse', 'HEAD^@']
        parent_hashes = tuple(subprocess.check_output(parent_cmd).decode().strip().split('\n'))

        # Clean up the state file
        os.remove(state_file)

        return GitCommitState(commit_hash, timestamp, StateType.QUANTUM, parent_hashes)

    def superpose(self, states: List[T]) -> 'QuantumStateRing[T]':
        """Create a superposition of multiple states"""
        for state in states:
            state_hash = hashlib.sha256(str(state).encode()).hexdigest()
            self.states[state_hash] = state
            commit_state = self._make_commit(state, "Superposition state")
            self._commit_map[state_hash] = commit_state

        # Create merkle root of superposed states
        self.current_state = self._create_merkle_root(list(self.states.keys()))
        return self

    def _create_merkle_root(self, hashes: List[str]) -> str:
        """Create a merkle root from a list of state hashes"""
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
            next_level = []
            for i in range(0, len(hashes), 2):
                combined = hashlib.sha256(
                    (hashes[i] + hashes[i + 1]).encode()
                ).hexdigest()
                next_level.append(combined)
            hashes = next_level
        return hashes[0] if hashes else ""

    def collapse(self, condition: Callable[[T], bool]) -> T:
        """Collapse superposition based on a condition"""
        valid_states = {
            h: s for h, s in self.states.items() 
            if condition(s)
        }

        if not valid_states:
            raise ValueError("No states satisfy the collapse condition")

        # Take the first valid state (could be randomized)
        state_hash, state = next(iter(valid_states.items()))
        self.current_state = state_hash

        # Record collapse in git
        commit_state = self._make_commit(state, "State collapse")
        self._commit_map[state_hash] = commit_state

        return state

    def traverse_ring(self, steps: int) -> List[T]:
        """Traverse the state ring by number of steps"""
        if not self.current_state:
            raise ValueError("No current state")

        current = self._commit_map.get(self.current_state)
        history = []

        for _ in range(steps):
            if not current or not current.parent_hashes:
                break

            parent_hash = current.parent_hashes[0]
            parent_state = self._get_state_from_commit(parent_hash)
            if parent_state:
                history.append(parent_state)

            current = self._commit_map.get(parent_hash)

        return history

    def _get_state_from_commit(self, commit_hash: str) -> Optional[T]:
        """Retrieve state from a git commit"""
        try:
            show_cmd = ['git', 'show', f'{commit_hash}:state.json']
            state_data = subprocess.check_output(show_cmd).decode()
            # Assuming state can be reconstructed from JSON
            return json.loads(state_data)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return None

    def _is_git_repo(self) -> bool:
        """Check if the current directory is a valid Git repository"""
        try:
            subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

# Example usage
if __name__ == "__main__":
    qsr = QuantumStateRing[int]()
    qsr.superpose([1, 2, 3])
    collapsed_state = qsr.collapse(lambda x: x > 1)
    print(collapsed_state)
    history = qsr.traverse_ring(2)
    print(history)