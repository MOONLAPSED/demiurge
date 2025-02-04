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
        return Ψ(lambda p: sum((self.f(x) * exp(-2j * pi * x * p)).real for x in range(-100, 100)))  # Use real part of the product

    def normalize(self):
        """Normalization operation (ensuring unit integral if interpreted as probability density)."""
        norm = sum(abs(self.f(x))**2 for x in range(-100, 100))**0.5
        return Ψ(lambda x: self.f(x) / norm if norm else 0)

class Ψ_1(Ψ):
    # Position and Momentum Representations
    X = Ψ(lambda x: x)   # Position observable
    P = X.fourier()      # Momentum observable via Fourier transform

    # Perturbation of X & P
    def perturb(f):
        return Ψ(lambda x: f(x) * X.f(x))

    def perturb_fourier(f):
        return Ψ(lambda p: (f(p) * P.f(p)).real)  # Return the real part

def main():
    psi1 = Ψ(lambda x: exp(-x**2))  # Gaussian wavefunction
    psi2 = Ψ(lambda x: exp(-x**2) * 2)
    psi3 = psi1 + psi2  # Superposition of two wavefunctions
    psi4 = psi1 * psi2  # Tensor product of two wavefunctions
    
    print(f"psi1 for x=0: {psi1.f(0)}")  # Evaluate psi1 at x=0
    for i in range (-10, 11):
        print(psi1.f(i))  # Evaluate psi1 at x=i
    print(f"psi2 for x=0: {psi2.f(0)}")
    for i in range (-10, 11):
        print(psi2.f(i))
    print(f"psi3 for x=0: {psi3.f(0)}")
    for i in range (-10, 11):
        print(psi3.f(i))

if __name__ == "__main__":
    main()