import decimal
import math
import inspect
import weakref

# ------------------------------------------------------------------------------
# Setup Decimal Context for Arbitrary Precision
# ------------------------------------------------------------------------------
decimal.getcontext().prec = 50  # Start with high precision; can change dynamically

# ------------------------------------------------------------------------------
# ComplexUnitCircle: Hard-Math Hook for Arbitrary Precision Complex Numbers
# ------------------------------------------------------------------------------
class ComplexUnitCircle:
    def __init__(self, real, imag, precision=None):
        # Initialize with real and imaginary parts as Decimals.
        self.real = decimal.Decimal(real)
        self.imag = decimal.Decimal(imag)
        # Adjust precision if provided.
        if precision is not None:
            decimal.getcontext().prec = precision
        self.normalize()
        
    def normalize(self):
        """Ensure that the complex number lies on the unit circle (magnitude = 1)."""
        magnitude = (self.real**2 + self.imag**2).sqrt()
        if magnitude == 0:
            self.real, self.imag = decimal.Decimal(1), decimal.Decimal(0)
        else:
            self.real /= magnitude
            self.imag /= magnitude
        
    def rotate(self, angle_degrees):
        """Rotate the complex number by a given angle (in degrees) on the unit circle."""
        # Convert degrees to radians.
        angle_radians = decimal.Decimal(angle_degrees) * (decimal.Decimal(math.pi) / decimal.Decimal(180))
        # For our trig functions, we use the math module on float values,
        # then convert back to Decimal.
        cos_angle = decimal.Decimal(math.cos(float(angle_radians)))
        sin_angle = decimal.Decimal(math.sin(float(angle_radians)))
        
        new_real = self.real * cos_angle - self.imag * sin_angle
        new_imag = self.real * sin_angle + self.imag * cos_angle
        
        self.real = new_real
        self.imag = new_imag
        self.normalize()
        
    def __add__(self, other):
        return ComplexUnitCircle(self.real + other.real, self.imag + other.imag)
    
    def __mul__(self, other):
        # Complex multiplication: (a+bi)*(c+di)
        new_real = self.real * other.real - self.imag * other.imag
        new_imag = self.real * other.imag + self.imag * other.real
        return ComplexUnitCircle(new_real, new_imag)
    
    def __repr__(self):
        prec = decimal.getcontext().prec
        # Format the Decimal values using the current precision.
        return f"ComplexUnitCircle(real={self.real:.{prec}f}, imag={self.imag:.{prec}f})"
    
    def abs(self):
        # Compute magnitude
        return (self.real**2 + self.imag**2).sqrt()
    
    def copy(self):
        return ComplexUnitCircle(self.real, self.imag)

# ------------------------------------------------------------------------------
# Epigenetic Kernel Q Using ComplexUnitCircle as Its Underlying Type
# ------------------------------------------------------------------------------
class Q:
    """
    Epigenetic Kernel State with two operators:
    ψ (novelty) and π (momentum).
    The state is represented as a ComplexUnitCircle.
    """
    def __init__(self, state: ComplexUnitCircle, ψ, π):
        self.state = state  # A ComplexUnitCircle instance
        self.ψ = ψ  # Function: ComplexUnitCircle -> ComplexUnitCircle
        self.π = π  # Function: ComplexUnitCircle -> ComplexUnitCircle

    def free_energy(self, P=ComplexUnitCircle(1, 0)):
        """
        A toy free energy calculation. Here we use the magnitude of the state as a proxy.
        Since our state is normalized (magnitude=1), this will be small, but we can
        still introduce a slight correction.
        """
        Q_prob = self.state.abs()
        # Avoid log(0) by clamping to a small value.
        Q_prob = Q_prob if Q_prob != 0 else decimal.Decimal('1e-9')
        P_prob = P.abs() if P.abs() != 0 else decimal.Decimal('1e-9')
        # Compute a simple difference in log space.
        return Q_prob * (Q_prob.ln() - P_prob.ln())

    def normalize(self, P=ComplexUnitCircle(1, 0)):
        """
        Normalize the state to lie on the unit circle while adjusting based on free energy.
        """
        new_val = self.ψ(self.state.copy()) + self.π(self.state.copy())
        norm = new_val.abs()
        if norm == 0:
            self.state = P
        else:
            fe = self.free_energy(P)
            # Adjust the real and imaginary parts according to the free energy correction.
            new_real = new_val.real / norm * (decimal.Decimal(1) - fe)
            new_imag = new_val.imag / norm * (decimal.Decimal(1) - fe)
            self.state = ComplexUnitCircle(new_real, new_imag)
        return self

    def evolve(self):
        """
        Evolve the kernel by applying ψ and π, then re-normalize.
        """
        new_state = self.ψ(self.state.copy()) + self.π(self.state.copy())
        new_q = Q(new_state, self.ψ, self.π)
        new_q.normalize()
        return new_q

    def __repr__(self):
        return f"Q(state={self.state}, ψ={self.ψ.__name__}, π={self.π.__name__})"

# ------------------------------------------------------------------------------
# Overload the addition operator for ComplexUnitCircle outside the class definition
# (This enables using the '+' operator directly on our ComplexUnitCircle instances.)
def add_complex(a: ComplexUnitCircle, b: ComplexUnitCircle) -> ComplexUnitCircle:
    new_real = a.real + b.real
    new_imag = a.imag + b.imag
    return ComplexUnitCircle(new_real, new_imag)

# Monkey-patch the __add__ method (if not already defined)
ComplexUnitCircle.__add__ = add_complex

# ------------------------------------------------------------------------------
# Entropy-Sensitive Operators (ψ and π) for ComplexUnitCircle
# ------------------------------------------------------------------------------
def entropy(x: ComplexUnitCircle):
    """
    A toy entropy function using the magnitude of x.
    Since x is normalized (|x|=1), we use a placeholder entropy value.
    """
    # For demonstration, let entropy vary slightly with the real part.
    return -(x.real.ln() if x.real > 0 else decimal.Decimal('0'))

def novel(x: ComplexUnitCircle) -> ComplexUnitCircle:
    """
    ψ: Introduces novelty via a rotation modulated by an entropy-like factor.
    """
    # Rotate by an angle proportional to our toy entropy function.
    angle = decimal.Decimal('0.1') * entropy(x)
    new_x = x.copy()
    new_x.rotate(float(angle))  # Convert angle to float for rotation
    return new_x

def inertia(x: ComplexUnitCircle) -> ComplexUnitCircle:
    """
    π: Provides momentum by applying a slight damping (or scaling) based on entropy.
    """
    # For demonstration, we dampen the state slightly.
    # Create a new ComplexUnitCircle with scaled real and imag.
    scale = decimal.Decimal('0.95') + decimal.Decimal('0.05') * (entropy(x).copy_abs())
    return ComplexUnitCircle(x.real * scale, x.imag * scale)

# ------------------------------------------------------------------------------
# Entanglement: Two Q Kernels Sharing Information
# ------------------------------------------------------------------------------
class EntangledQ:
    """
    Two entangled Q kernels that mix their states according to a set strength.
    """
    def __init__(self, q1: Q, q2: Q, entanglement_strength: decimal.Decimal = decimal.Decimal('0.5')):
        self.q1 = q1
        self.q2 = q2
        # Clamp entanglement_strength between 0 and 1.
        self.entanglement_strength = max(decimal.Decimal('0'), min(entanglement_strength, decimal.Decimal('1')))

    def entangle(self):
        s1, s2 = self.q1.state, self.q2.state
        strength = self.entanglement_strength
        # Mix the states based on entanglement strength.
        new_state1 = s1 * (decimal.Decimal(1) - strength) + s2 * strength
        new_state2 = s2 * (decimal.Decimal(1) - strength) + s1 * strength
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

# ------------------------------------------------------------------------------
# Modified Quine: Self-Reflective, Self-Modifying Code
# ------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------
# Demonstration: Q, Entanglement, and Modified Quines Using Decimal-based ComplexUnitCircle
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Create two Q kernels with ComplexUnitCircle states.
    q1 = Q(ComplexUnitCircle('1', '0'), novel, inertia)
    q2 = Q(ComplexUnitCircle('0.8', '0.2'), novel, inertia)
    print("Initial Q states:")
    print(q1)
    print(q2)

    # Entangle and evolve them:
    entangled = EntangledQ(q1, q2, entanglement_strength=decimal.Decimal('0.6'))
    for i in range(5):
        entangled.evolve()
        print(f"Evolution {i+1}: {entangled}")

    # Instantiate and run a Modified Quine:
    mq = ModifiedQuine()
    print("\nOriginal ModifiedQuine:")
    print(mq)
    # Example transformation: Append a comment to the source code.
    def add_comment(source: str) -> str:
        return source + "\n# Epigenetic modification applied!"
    mq.modify(add_comment)
    mq.run()
