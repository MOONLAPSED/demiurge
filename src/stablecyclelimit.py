from decimal import Decimal, getcontext
import math

getcontext().prec = 28  # High precision for stability

#############################################
# Minimal Complex Arithmetic with Decimal
#############################################
class ComplexDecimal:
    def __init__(self, real, imag=Decimal('0')):
        self.real = Decimal(real)
        self.imag = Decimal(imag)
    
    def __add__(self, other):
        return ComplexDecimal(self.real + other.real, self.imag + other.imag)
    
    def __sub__(self, other):
        return ComplexDecimal(self.real - other.real, self.imag - other.imag)
    
    def __mul__(self, other):
        return ComplexDecimal(
            self.real * other.real - self.imag * other.imag,
            self.real * other.imag + self.imag * other.real
        )
    
    def __truediv__(self, other):
        denom = other.real * other.real + other.imag * other.imag
        num = self * other.conjugate()
        return ComplexDecimal(num.real / denom, num.imag / denom)
    
    def conjugate(self):
        return ComplexDecimal(self.real, -self.imag)
    
    def abs(self):
        return (self.real * self.real + self.imag * self.imag).sqrt()
    
    def __repr__(self):
        return f"({self.real}+{self.imag}i)"

#############################################
# Epistemic Phase Space Kernel (Q)
#############################################
class Q:
    """
    Epistemic feedback kernel.
    - ψ: Injects novelty (perturbation)
    - π: Applies damping (momentum retention)
    """
    def __init__(self, state: ComplexDecimal, ψ, π):
        self.state = state
        self.ψ = ψ
        self.π = π

    def normalize(self):
        """Normalize state to a unit cycle with slight adaptive energy loss."""
        norm = self.state.abs()
        if norm > 0:
            self.state = ComplexDecimal(self.state.real / norm, self.state.imag / norm)
        return self

    def evolve(self):
        """Evolve with ψ and π, ensuring periodic attractor-like behavior."""
        new_state = self.ψ(self.state) + self.π(self.state)
        self.state = new_state
        return self.normalize()

    def __repr__(self):
        return f"Q(state={self.state})"

#############################################
# ψ (Novelty) - Oscillatory Phase Perturbation
#############################################
def novel(x: ComplexDecimal) -> ComplexDecimal:
    """
    Introduces an oscillatory perturbation using a rotational factor.
    """
    angle = Decimal('0.1')  # Small rotation factor
    rot = ComplexDecimal(d_cos(angle), d_sin(angle))  # e^(iθ)
    return x * rot

#############################################
# π (Momentum) - Nonlinear Damping
#############################################
def inertia(x: ComplexDecimal) -> ComplexDecimal:
    """
    Applies non-linear damping to stabilize limit cycle behavior.
    """
    entropy = x.abs()  # Proxy for information density
    scaling = Decimal('0.98') + Decimal('0.02') * entropy  # Soft damping
    return ComplexDecimal(x.real * scaling, x.imag * scaling)

#############################################
# Decimal-Based Trig Functions (Taylor Series)
#############################################
def d_sin(x, terms=10):
    x = Decimal(x)
    result = Decimal(0)
    sign = Decimal(1)
    x_power = x
    factorial = Decimal(1)
    for n in range(1, 2*terms, 2):
        result += sign * x_power / factorial
        sign *= -1
        x_power *= x * x
        factorial *= Decimal(n+1) * Decimal(n+2)
    return result

def d_cos(x, terms=10):
    x = Decimal(x)
    result = Decimal(0)
    sign = Decimal(1)
    x_power = Decimal(1)
    factorial = Decimal(1)
    for n in range(0, 2*terms, 2):
        result += sign * x_power / factorial
        sign *= -1
        x_power *= x * x
        factorial *= Decimal(n+1) * Decimal(n+2)
    return result

#############################################
# Run the System: Observe Limit Cycles
#############################################
if __name__ == "__main__":
    q = Q(ComplexDecimal('1', '0'), novel, inertia)

    print("Initial Q state:")
    print(q)

    for i in range(2000):
        q.evolve()
        print(f"Step {i+1}: {q}")
