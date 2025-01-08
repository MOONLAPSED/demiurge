#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import random
from typing import List, Callable, Dict, Any
from enum import Enum, auto
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Enum representing possible conditions/actions
class Condition(Enum):
    A = auto()
    B = auto()
    C = auto()
    D = auto()
    E = auto()
    F = auto()
    G = auto()
    H = auto()

# Class representing an action or reaction
class Reaction:
    def __init__(self, inputs: List[Condition], outputs: List[Condition], agency_name: str):
        self.inputs = inputs
        self.outputs = outputs
        self.agency_name = agency_name

    def __str__(self):
        inputs_str = ', '.join([condition.name for condition in self.inputs])
        outputs_str = ', '.join([condition.name for condition in self.outputs])
        return f"{self.agency_name}: {inputs_str} → {outputs_str}"

# Agency class that can perform actions
class Agency:
    def __init__(self, name: str):
        self.name = name
        self.rules = []  # A list of reactions this agency can catalyze

    def add_rule(self, inputs: List[Condition], outputs: List[Condition]):
        reaction = Reaction(inputs, outputs, self.name)
        self.rules.append(reaction)

    def perform(self, environment: List[Condition]):
        logger.debug(f"{self.name} is assessing the environment: {[c.name for c in environment]}")
        for rule in self.rules:
            if all(condition in environment for condition in rule.inputs):
                logger.info(f"Performing: {rule}")
                # Add outputs to the environment, replacing inputs
                for condition in rule.inputs:
                    environment.remove(condition)
                environment.extend(rule.outputs)
                return rule.outputs  # Break after performing one rule

    def __str__(self):
        return f"Agency {self.name}"

# Function to simulate the process
def simulate(agencies: List[Agency], iterations: int = 10):
    environment = [random.choice(list(Condition)) for _ in range(4)]
    for _ in range(iterations):
        logger.info(f"Current environment state: {[c.name for c in environment]}")
        for agency in agencies:
            agency.perform(environment)
        logger.info(f"Environment after interactions: {[c.name for c in environment]}")

def main():
    # Create agencies with some sample rules
    agency_x = Agency("Agency_X")
    agency_x.add_rule([Condition.A, Condition.B], [Condition.C])
    agency_x.add_rule([Condition.C], [Condition.D, Condition.E])

    agency_y = Agency("Agency_Y")
    agency_y.add_rule([Condition.D], [Condition.F])
    agency_y.add_rule([Condition.E, Condition.F], [Condition.G])

    # Simulate the dynamic interaction
    simulate(agencies=[agency_x, agency_y])

if __name__ == "__main__":
    main()