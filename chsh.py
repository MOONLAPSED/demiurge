import math
import random

class EntangledPhoton:
    def __init__(self):
        # No state is stored; entanglement is implicit in measurement outcomes
        pass

    def measure(self, angle_a: float, angle_b: float) -> tuple[int, int]:
        """
        Simulate a measurement of two entangled photons at angles `angle_a` and `angle_b`.
        Returns a tuple of results (-1 or +1) for Alice and Bob.
        """
        # Calculate the probability of correlated outcomes based on quantum mechanics
        delta = angle_a - angle_b
        prob_same = math.cos(delta) ** 2  # Quantum correlation probability

        # Determine outcomes
        same_outcome = random.random() < prob_same
        result_a = random.choice([-1, 1])
        result_b = result_a if same_outcome else -result_a
        return result_a, result_b


def simulate_chsh_trials(trials: int) -> float:
    """
    Simulate a CHSH Bell test and calculate the CHSH value.
    """
    angles = [
        (0, math.pi / 4),         # Alice chooses 0°, Bob chooses 45°
        (0, -math.pi / 4),        # Alice chooses 0°, Bob chooses -45°
        (math.pi / 2, math.pi / 4),  # Alice chooses 90°, Bob chooses 45°
        (math.pi / 2, -math.pi / 4)  # Alice chooses 90°, Bob chooses -45°
    ]
    
    counts = [0, 0, 0, 0]
    entangled_photon = EntangledPhoton()

    for i in range(trials):
        for idx, (angle_a, angle_b) in enumerate(angles):
            result_a, result_b = entangled_photon.measure(angle_a, angle_b)
            counts[idx] += result_a * result_b  # Correlation is the product of results

    # Calculate CHSH value
    s = (counts[0] + counts[1] + counts[2] - counts[3]) / trials
    return s


if __name__ == "__main__":
    trials = 10000
    chsh_value = simulate_chsh_trials(trials)
    print(f"Simulated CHSH value: {chsh_value}")
    print("Bell's Inequality violated!" if abs(chsh_value) > 2 else "No violation.")
