from typing import List, Optional, Callable, Tuple, Union, Protocol, TypeVar, Generic, Any
import math
import itertools
import heapq

T = TypeVar('T')

class QuantumState(Generic[T]):
    def __init__(self, possibilities: List[T], amplitudes: Optional[List[float]] = None):
        n = len(possibilities)
        self.possibilities = possibilities
        if amplitudes is None:
            self.amplitudes = [1 / math.sqrt(n)] * n
        else:
            if len(amplitudes) != n or not math.isclose(sum(amplitudes), 1.0):
                raise ValueError("Amplitudes must sum to 1 and match the number of possibilities.")
            self.amplitudes = amplitudes

    def entangle(self, other: "QuantumState") -> "QuantumState":
        new_possibilities = [p1 + p2 for p1 in self.possibilities for p2 in other.possibilities]
        new_amplitudes = [a1 * a2 for a1 in self.amplitudes for a2 in other.amplitudes]
        normalization_factor = sum(new_amplitudes)
        new_amplitudes = [a / normalization_factor for a in new_amplitudes]
        return QuantumState(new_possibilities, new_amplitudes)

class MaxwellDemon:
    def __init__(self, particles: List[float], energy_threshold: float):
        self.particles = particles
        self.energy_threshold = energy_threshold
        self.high_energy = [p for p in particles if p > energy_threshold]
        self.low_energy = [p for p in particles if p <= energy_threshold]

    def update_threshold(self, new_threshold: float) -> None:
        self.energy_threshold = new_threshold
        self.high_energy = [p for p in self.particles if p > new_threshold]
        self.low_energy = [p for p in self.particles if p <= new_threshold]

    def visualize_sorted(self) -> None:
        print("High Energy:", list(self.high_energy))
        print("Low Energy:", list(self.low_energy))

class SKICombinator:
    @staticmethod
    def S(f: Callable[..., Any], g: Callable[..., Any], x: Any) -> Any:
        if not callable(f) or not callable(g):
            raise TypeError("Both f and g must be callable.")
        return f(x)(g(x))

    @staticmethod
    def B(f: Callable[..., Any], g: Callable[..., Any], x: Any) -> Any:
        return f(g(x))

    @staticmethod
    def C(f: Callable[..., Any], x: Any, y: Any) -> Any:
        return f(y)(x)

class MorphologicalTree:
    def __init__(self, nodes: List['MorphologicalNode']):
        self.root = self.build_tree(nodes)

    def build_tree(self, nodes: List['MorphologicalNode']) -> 'InternalNode':
        heap = [(node.hash, node) for node in nodes]
        heapq.heapify(heap)
        while len(heap) > 1:
            _, left = heapq.heappop(heap)
            _, right = heapq.heappop(heap)
            combined_node = InternalNode(left=left, right=right)
            heapq.heappush(heap, (combined_node.hash, combined_node))
        return heapq.heappop(heap)[1]

    def visualize(self) -> None:
        print("Tree root:", self.root.hash)

class InternalNode:
    def __init__(self, left: 'MorphologicalNode', right: 'MorphologicalNode'):
        self.left = left
        self.right = right
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> int:
        return hash((self.left.hash, self.right.hash))

class MorphologicalNode:
    def __init__(self, data: str):
        self.data = data
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> int:
        return hash(self.data)

# Example usage
quantum_state_1 = QuantumState(['0', '1'])
quantum_state_2 = QuantumState(['+', '-'])
entangled_state = quantum_state_1.entangle(quantum_state_2)

demon = MaxwellDemon([1.0, 0.9, 0.2, 0.5], 0.5)
demon.update_threshold(0.7)
demon.visualize_sorted()

morph_nodes = [MorphologicalNode('a'), MorphologicalNode('b'), MorphologicalNode('c')]
morph_tree = MorphologicalTree(morph_nodes)
morph_tree.visualize()
