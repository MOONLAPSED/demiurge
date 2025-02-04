import cmath
import math
import random
import weakref

# === Q: The Epigenetic Kernel State ===

class Q:
    """
    Epigenetic kernel state with emergent novelty (ψ) and computational momentum (π).
    Q encapsulates both its own state and its evolution operators.
    """
    def __init__(self, state, ψ, π):
        self.state = state  # The current computational state (complex number, function, or data)
        self.ψ = ψ          # Novelty operator (exploration)
        self.π = π          # Inertia operator (exploitation/stability)
        self.history = [state]  # Record of past states for epigenetic feedback

    def free_energy(self, P=1.0):
        """Compute a proxy free energy (KL divergence-like measure) relative to expected prior P."""
        Q_val = abs(self.state)
        fe = Q_val * math.log((Q_val + 1e-9) / (abs(P) + 1e-9))
        return fe

    def normalize(self, P=1.0):
        """Normalize the state to remain within a computationally viable manifold (minimizing free energy)."""
        norm = abs(self.ψ(self.state) + self.π(self.state))
        if norm == 0:
            self.state = P  # Self-healing: reset to prior if collapse occurs
        else:
            fe = self.free_energy(P)
            self.state = (self.state / norm) * (1 - fe)
        return self.state

    def evolve(self):
        """Evolve Q using its current ψ and π operators, applying normalization and history tracking."""
        new_state = self.ψ(self.state) + self.π(self.state)
        evolved = Q(new_state, self.ψ, self.π)
        evolved.history = self.history + [new_state]
        evolved.normalize()
        return evolved

    def entangle(self, other):
        """Entangle with another Q instance, linking states via an epigenetic coupling."""
        combined_state = (self.state + other.state) / 2
        new_ψ = lambda x: (self.ψ(x) + other.ψ(x)) / 2
        new_π = lambda x: (self.π(x) + other.π(x)) / 2
        entangled_Q = Q(combined_state, new_ψ, new_π)
        entangled_Q.history = self.history + other.history + [combined_state]
        return entangled_Q

    def self_modify(self, modifier):
        """Self-reflect and modify its evolution operators using an external modifier function."""
        new_ψ, new_π = modifier(self.ψ, self.π, self.history)
        self.ψ, self.π = new_ψ, new_π

    def __repr__(self):
        return f"Q(state={self.state:.3f}, history_len={len(self.history)})"


# === Example Operators (ψ and π) with Entropy Influence ===

def entropy(x):
    """A naive Shannon entropy-like measure for a scalar state."""
    prob = abs(x) / (abs(x) + 1e-9)
    return -prob * math.log(prob + 1e-9)

def novel(x):
    """Novelty operator: introduces a controlled complex rotation influenced by 'entropy'."""
    return x * cmath.exp(1j * (0.1 + 0.05 * entropy(x)))

def inertia(x):
    """Inertia operator: dampens the state while allowing some entropy-driven modulation."""
    return x * (0.95 + 0.05 * entropy(x))


# === A Modifier Function for Self-Modification ===

def epigenetic_modifier(ψ, π, history):
    """Modify ψ and π based on the system's history to regulate novelty and stability."""
    avg_state = sum(abs(s) for s in history) / len(history)
    new_ψ = lambda x: ψ(x) * (0.9 if avg_state > 1.0 else 1.0)
    new_π = lambda x: π(x) * (1.05 if avg_state > 1.0 else 1.0)
    return new_ψ, new_π


# === Testing the Q Kernel ===

q1 = Q(1 + 0j, novel, inertia)
q2 = Q(0.8 + 0.2j, novel, inertia)

print("Initial q1:", q1)
print("Initial q2:", q2)

# Evolve them individually:
q1_evolved = q1.evolve()
q2_evolved = q2.evolve()
print("Evolved q1:", q1_evolved)
print("Evolved q2:", q2_evolved)

# Entangle q1 and q2:
q_entangled = q1_evolved.entangle(q2_evolved)
print("Entangled Q:", q_entangled)

# Let the entangled Q self-modify:
q_entangled.self_modify(epigenetic_modifier)
print("Self-modified Entangled Q:", q_entangled)

# Iterate evolution in a loop:
for i in range(5):
    q_entangled = q_entangled.evolve()
    print(f"Iteration {i+1}:", q_entangled)
