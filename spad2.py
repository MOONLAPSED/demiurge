import random
import cmath

class QuantumField:
    def __init__(self, field_type, dimension, energy=None):
        self.field_type = field_type  # 'photon', 'electron', 'baryon', etc.
        self.dimension = dimension
        self.energy = energy or random.uniform(1.0, 10.0)  # Energy of the quantum field
        self.normal_vector = self._generate_normal_vector()

    def _generate_normal_vector(self):
        """Generate a random unit vector in complex space representing the dipole direction."""
        angle = random.uniform(0, 2 * cmath.pi)
        return cmath.rect(1, angle)  # unit complex number (magnitude 1)

    def interact_with_medium(self, medium):
        """Photon interacts with a nonlinear medium for parametric down-conversion."""
        if self.field_type == 'photon':
            return medium.process_photon(self)
        raise ValueError("Only photons can interact with the nonlinear medium.")

class NonlinearMedium:
    def __init__(self, efficiency=0.8):
        self.efficiency = efficiency  # Probability that a photon will split

    def process_photon(self, photon):
        """Perform parametric down-conversion on the incoming photon."""
        if random.random() <= self.efficiency:
            # Conserve energy by splitting the photon into two with half energy each
            signal_photon = QuantumField('photon', photon.dimension, energy=photon.energy / 2)
            idler_photon = QuantumField('photon', photon.dimension, energy=photon.energy / 2)
            print(f"Photon with energy {photon.energy:.2f} splits into:")
            print(f"  Signal Photon: Energy = {signal_photon.energy:.2f}, Normal = {signal_photon.normal_vector}")
            print(f"  Idler Photon: Energy = {idler_photon.energy:.2f}, Normal = {idler_photon.normal_vector}")
            return signal_photon, idler_photon
        else:
            print("Photon did not undergo down-conversion.")
            return photon, None

# Main simulation for parametric down-conversion
def main():
    # Create a high-energy photon
    pump_photon = QuantumField('photon', 1, energy=5.0)
    print(f"Incoming Photon: Energy = {pump_photon.energy:.2f}, Normal = {pump_photon.normal_vector}")

    # Create a nonlinear medium
    crystal = NonlinearMedium(efficiency=0.9)

    # Perform parametric down-conversion
    signal_photon, idler_photon = pump_photon.interact_with_medium(crystal)

    # Print results
    if idler_photon:
        print("Parametric down-conversion successful!")
    else:
        print("No down-conversion occurred.")

if __name__ == "__main__":
    main()
