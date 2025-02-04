from decimal import Decimal, getcontext
import math

getcontext().prec = 28

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

def d_sin(x, terms=10):
    x = Decimal(x)
    result = Decimal(0)
    sign = Decimal(1)
    x_power = x
    factorial = Decimal(1)
    for n in range(1, 2 * terms, 2):
        result += sign * x_power / factorial
        sign *= -1
        x_power *= x * x
        factorial *= Decimal(n + 1) * Decimal(n + 2)
    return result

def d_cos(x, terms=10):
    x = Decimal(x)
    result = Decimal(0)
    sign = Decimal(1)
    x_power = Decimal(1)
    factorial = Decimal(1)
    for n in range(0, 2 * terms, 2):
        result += sign * x_power / factorial
        sign *= -1
        x_power *= x * x
        factorial *= Decimal(n + 1) * Decimal(n + 2)
    return result

def cexp(z: ComplexDecimal) -> ComplexDecimal:
    a = z.real
    b = z.imag
    exp_a = a.exp()
    return ComplexDecimal(exp_a * d_cos(b), exp_a * d_sin(b))

class Q:
    def __init__(self, state: ComplexDecimal, ψ, π, λ=Decimal('0.9')):
        self.state = state
        self.ψ = ψ
        self.π = π
        self.λ = λ  
        self.history = [state]

    def entropy(self):
        p = self.state.abs()
        return -(p * p.ln() if p != 0 else Decimal('1e-9'))

    def normalize(self):
        norm = self.state.abs()
        if norm != 0:
            self.state = ComplexDecimal(self.state.real / norm, self.state.imag / norm)
        return self

    def evolve(self):
        past_influence = self.history[-1] * ComplexDecimal(self.λ, 0)  
        self.state = self.ψ(self.state) + self.π(self.state) + past_influence
        self.normalize()
        self.history.append(self.state)
        if len(self.history) > 10:
            self.history.pop(0)  
        return self

    def __repr__(self):
        return f"Q(state={self.state})"

def novel(x: ComplexDecimal) -> ComplexDecimal:
    angle = Decimal('0.2') * d_sin(x.real)  
    rot = cexp(ComplexDecimal(0, angle))
    return x * rot

def inertia(x: ComplexDecimal) -> ComplexDecimal:
    scale = Decimal('0.98') + Decimal('0.02') * x.abs()
    return ComplexDecimal(x.real * scale, x.imag * scale)

# Q1 and Q2 will form a bounded attractor system:
q1 = Q(ComplexDecimal('1', '0'), novel, inertia)
q2 = Q(ComplexDecimal('0.8', '0.2'), novel, inertia)

for i in range(50000):
    q1.evolve()
    q2.evolve()
    print(f"Step {i+1}: {q1}, {q2}")
