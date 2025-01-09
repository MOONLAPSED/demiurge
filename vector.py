import math

class Vector:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar):
        if scalar == 0:
            raise ValueError("Cannot divide by zero.")
        return Vector(self.x / scalar, self.y / scalar, self.z / scalar)

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            raise ValueError("Cannot normalize a zero vector.")
        return self / mag

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y}, z={self.z})"

v1 = Vector(1, 2, 3)
v2 = Vector(4, 5, 6)

v3 = v1 + v2
v4 = v1 - v2
v5 = v1 * 2
v6 = v1 / 2

dot_product = v1.dot(v2)
cross_product = v1.cross(v2)

print(f"v1 + v2: {v3}")
print(f"v1 - v2: {v4}")
print(f"v1 * 2: {v5}")
print(f"v1 / 2: {v6}")
print(f"Dot product: {dot_product}")
print(f"Cross product: {cross_product}")
