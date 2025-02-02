from functools import lru_cache
from math import exp, pi

class Ψ:
    """Wavefunction-like class, a mapping Ψ(x) -> Ψ'(x) under transformation."""
    def __init__(self, f): 
        """Initialize with a function f(x)."""
        self.f = f  

    def __call__(self, x):  
        """Evaluate wavefunction at x."""
        return self.f(x)

    def __mul__(self, other):  
        """Tensor-like interaction: Ψ ⊗ Ψ'"""
        return Ψ(lambda x: self.f(x) * other.f(x))

    def __add__(self, other):
        """Superposition principle: Ψ + Ψ'"""
        return Ψ(lambda x: self.f(x) + other.f(x))

    def fourier(self):
        """Fourier transform for shifting between position & momentum representations."""
        return Ψ(lambda p: sum(self.f(x) * exp(-2j * pi * x * p) for x in range(-100, 100)))

    def normalize(self):
        """Normalization operation (ensuring unit integral if interpreted as probability density)."""
        norm = sum(abs(self.f(x))**2 for x in range(-100, 100))**0.5
        return Ψ(lambda x: self.f(x) / norm if norm else 0)

# Position and Momentum Representations
X = Ψ(lambda x: x)   # Position observable
P = X.fourier()      # Momentum observable via Fourier transform

if __name__ == "__main__":
    print(f"{X}: {X(0)}")
    print({P.fourier})