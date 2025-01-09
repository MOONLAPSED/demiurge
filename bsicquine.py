class Computation:
    def __init__(self, func):
        self.func = func
        self.state = {}

    def __call__(self, *args, **kwargs):
        result = self.func(*args, **kwargs)
        self.update_state(args, kwargs, result)
        return result

    def update_state(self, args, kwargs, result):
        # Add logic to adapt the computation state
        self.state.update({
            'args': args,
            'kwargs': kwargs,
            'result': result
        })

    def compose(self, other):
        # Composition of two computational processes
        def composed(*args, **kwargs):
            first_result = self(*args, **kwargs)
            return other(first_result)
        return Computation(composed)

# Example computation
def increment(x):
    return x + 1

def double(x):
    return x * 2

# Creating computational primitives
comp1 = Computation(increment)
comp2 = Computation(double)

# Composing computations
composed_comp = comp1.compose(comp2)

# Executing a composed computation
result = composed_comp(3)  # (3 + 1) * 2 = 8
print("Result:", result)