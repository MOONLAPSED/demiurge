from enum import Enum, auto
from typing import List
import random
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Enum for conditions or states in the environment
class Condition(Enum):
    A = auto()
    B = auto()
    C = auto()
    D = auto()
    E = auto()
    F = auto()
    G = auto()
    H = auto()

# Reaction captures transformations in the environment
class Reaction:
    def __init__(self, inputs: List[Condition], outputs: List[Condition]):
        self.inputs = inputs
        self.outputs = outputs

    def __str__(self):
        return f"{self.inputs} --> {self.outputs}"

# Agency encapsulates the computational entity with reactive capability
class Agency:
    def __init__(self, name: str):
        self.name = name
        self.reactions = []  # Collection of reactions the agency can perform

    def add_rule(self, inputs: List[Condition], outputs: List[Condition]):
        self.reactions.append(Reaction(inputs, outputs))

    def perform(self, environment: List[Condition]) -> None:
        logger.debug(f"[{self.name}] assessing environment: {environment}")
        for reaction in self.reactions:
            if all(cond in environment for cond in reaction.inputs):
                logger.info(f"[{self.name}] performing reaction: {reaction}")
                # Transform environment
                for cond in reaction.inputs:
                    environment.remove(cond)
                environment.extend(reaction.outputs)
                break  # Perform one rule per iteration for simplicity

# Function to simulate the environment and the agents interacting within it
def simulate(agencies: List[Agency], iterations: int = 10):
    # Initial environmental conditions
    environment = [random.choice(list(Condition)) for _ in range(4)]
    for iteration in range(iterations):
        logger.info(f"Iteration {iteration+1}: Environment State = {environment}")
        for agency in agencies:
            agency.perform(environment)
        logger.info(f"Post-interaction Environment = {environment}")

def main():
    # Define agencies with rules
    agency_alpha = Agency("Alpha")
    agency_alpha.add_rule([Condition.A, Condition.B], [Condition.C])
    agency_alpha.add_rule([Condition.C], [Condition.D, Condition.E])

    agency_beta = Agency("Beta")
    agency_beta.add_rule([Condition.D], [Condition.F])
    agency_beta.add_rule([Condition.E, Condition.F], [Condition.G])

    # Conduct simulation
    simulate(agencies=[agency_alpha, agency_beta], iterations=10)

if __name__ == '__main__':
    main()