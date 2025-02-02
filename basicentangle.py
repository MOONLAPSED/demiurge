from decimal import Decimal, getcontext, ROUND_HALF_EVEN
import math, inspect, weakref

# Set a default precision (this can be modified at runtime)
getcontext().prec = 28

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
    
    def conjugate(self):
        return ComplexDecimal(self.real, -self.imag)
    
    def __truediv__(self, other):
        # a/b = a * conj(b) / |b|^2
        denom = other.real * other.real + other.imag * other.imag
        num = self * other.conjugate()
        return ComplexDecimal(num.real / denom, num.imag / denom)
    
    def abs(self):
        return (self.real * self.real + self.imag * self.imag).sqrt()
    
    def __repr__(self):
        return f"({self.real}+{self.imag}i)"

#############################################
# Decimal-based Trigonometric Functions (Taylor Series)
#############################################
def d_sin(x, terms=10):
    """
    Compute sin(x) using a Taylor series.
    x is expected to be a Decimal (representing radians).
    """
    x = Decimal(x)
    result = Decimal(0)
    sign = Decimal(1)
    x_power = x
    factorial = Decimal(1)
    for n in range(1, 2*terms, 2):
        result += sign * x_power / factorial
        sign *= -1
        # Increase power: multiply by x^2
        x_power *= x * x
        # Increase factorial: (n+1)*(n+2)
        factorial *= Decimal(n+1) * Decimal(n+2)
    return result

def d_cos(x, terms=10):
    """
    Compute cos(x) using a Taylor series.
    x is expected to be a Decimal (radians).
    """
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

def cexp(z: ComplexDecimal) -> ComplexDecimal:
    """
    Compute the complex exponential: exp(a+ib) = exp(a)*(cos(b) + i*sin(b))
    using Decimal arithmetic.
    """
    a = z.real
    b = z.imag
    exp_a = a.exp()  # Decimal.exp() gives exp for Decimal a
    cos_b = d_cos(b)
    sin_b = d_sin(b)
    return ComplexDecimal(exp_a * cos_b, exp_a * sin_b)

#############################################
# Epigenetic Kernel Q Using ComplexDecimal
#############################################
class Q:
    """
    Epigenetic Kernel State with two operators:
    ψ (novelty) and π (momentum).
    The state is a ComplexDecimal representing a point on the unit circle.
    """
    def __init__(self, state: ComplexDecimal, ψ, π):
        self.state = state  # ComplexDecimal instance
        self.ψ = ψ  # A function: ComplexDecimal -> ComplexDecimal
        self.π = π  # A function: ComplexDecimal -> ComplexDecimal

    def free_energy(self, P=ComplexDecimal(1)):
        """
        A toy free energy (KL divergence-like) calculation.
        Uses the magnitude of the state as a proxy.
        """
        Q_prob = self.state.abs()
        # Avoid log(0): if Q_prob is zero, use a tiny value.
        Q_prob = Q_prob if Q_prob != 0 else Decimal('1e-9')
        P_prob = P.abs() if P.abs() != 0 else Decimal('1e-9')
        return Q_prob * (Q_prob.ln() - P_prob.ln())

    def normalize(self, P=ComplexDecimal(1)):
        """
        Normalize the state to lie on a 'unit circle'
        while minimizing free energy.
        """
        new_val = self.ψ(self.state) + self.π(self.state)
        norm = new_val.abs()
        if norm == 0:
            self.state = P
        else:
            fe = self.free_energy(P)
            # Scale state to reduce "surprise" (fe) while normalizing.
            self.state = ComplexDecimal(new_val.real / norm * (1 - fe),
                                         new_val.imag / norm * (1 - fe))
        return self

    def evolve(self):
        """Evolve the kernel by applying ψ and π, then normalize."""
        new_state = self.ψ(self.state) + self.π(self.state)
        new_q = Q(new_state, self.ψ, self.π)
        new_q.normalize()
        return new_q

    def __repr__(self):
        return f"Q(state={self.state}, ψ={self.ψ.__name__}, π={self.π.__name__})"

#############################################
# Entropy-Sensitive Operators (ψ and π) for ComplexDecimal
#############################################
def entropy(x: ComplexDecimal, terms=10):
    """
    A toy entropy function using the magnitude of x.
    """
    p = x.abs()
    # p is a Decimal; avoid log(0)
    p = p if p != 0 else Decimal('1e-9')
    return -(p * p.ln())  # Negative for entropy

def novel(x: ComplexDecimal) -> ComplexDecimal:
    """
    ψ: Introduces novelty via a rotation modulated by entropy.
    """
    # Rotate by an angle proportional to entropy(x)
    angle = Decimal('0.1') * entropy(x)
    # Create a ComplexDecimal for exp(i*angle)
    rot = cexp(ComplexDecimal(0, angle))
    return x * rot

def inertia(x: ComplexDecimal) -> ComplexDecimal:
    """
    π: Provides momentum by dampening the state.
    """
    # Scale the state slightly based on entropy
    scale = Decimal('0.95') + Decimal('0.05') * entropy(x)
    return ComplexDecimal(x.real * scale, x.imag * scale)

#############################################
# Entanglement: Two Q Kernels Sharing Information
#############################################
class EntangledQ:
    """
    Two entangled Q kernels that mix their states according to a set strength.
    """
    def __init__(self, q1: Q, q2: Q, entanglement_strength: Decimal = Decimal('0.5')):
        self.q1 = q1
        self.q2 = q2
        # Clamp entanglement strength between 0 and 1.
        self.entanglement_strength = max(Decimal('0'), min(entanglement_strength, Decimal('1')))

    def entangle(self):
        s1, s2 = self.q1.state, self.q2.state
        strength = self.entanglement_strength
        new_state1 = s1 * (Decimal('1') - strength) + s2 * strength
        new_state2 = s2 * (Decimal('1') - strength) + s1 * strength
        self.q1.state = new_state1
        self.q2.state = new_state2
        self.q1.normalize()
        self.q2.normalize()

    def evolve(self):
        self.q1 = self.q1.evolve()
        self.q2 = self.q2.evolve()
        self.entangle()
        return self

    def __repr__(self):
        return f"EntangledQ(q1={self.q1}, q2={self.q2}, strength={self.entanglement_strength})"

#############################################
# Modified Quine: Self-Reflective, Self-Modifying Code
#############################################
class ModifiedQuine:
    """
    A self-reflective quine that can inspect and modify its own source code.
    """
    def __init__(self):
        self.source = inspect.getsource(self.__class__)

    def reflect(self):
        return self.source

    def modify(self, transformation):
        self.source = transformation(self.source)
        return self

    def run(self):
        print("Running ModifiedQuine with current source:")
        print(self.source)
        return self.source

    def __repr__(self):
        return f"ModifiedQuine(source_length={len(self.source)})"

#############################################
# Demonstration: Q, Entanglement, and Modified Quines Using Decimal
#############################################
if __name__ == "__main__":
    # Initialize two Q kernels with ComplexDecimal states:
    q1 = Q(ComplexDecimal('1', '0'), novel, inertia)
    q2 = Q(ComplexDecimal('0.8', '0.2'), novel, inertia)
    print("Initial Q states:")
    print(q1, q2)

    # Entangle and evolve them:
    entangled = EntangledQ(q1, q2, entanglement_strength=Decimal('0.6'))
    for i in range(5):
        entangled.evolve()
        print(f"Evolution {i+1}: {entangled}")

    # Create and run a Modified Quine:
    mq = ModifiedQuine()
    print("\nOriginal ModifiedQuine:")
    print(mq)
    # Example transformation: Append a comment to the source code.
    def add_comment(source: str) -> str:
        return source + "\n# Epigenetic modification applied!"
    mq.modify(add_comment)
    mq.run()
