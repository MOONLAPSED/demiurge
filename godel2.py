#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
import sys
from typing import List, Tuple, Dict

class TuringMachine:
    def __init__(self, 
                 states: List[str], 
                 tape_alphabet: List[str], 
                 tape: List[str],
                 blank: str, 
                 transitions: Dict[Tuple[str, str], Tuple[str, str, str]],
                 start_state: str, 
                 accept_state: str,
                 reject_state: str,
                 initial_godel: int = None):
        self.states = states
        self.tape_alphabet = tape_alphabet
        self.blank = blank
        self.transitions = transitions
        self.accept_state = accept_state
        self.reject_state = reject_state
        
        if initial_godel is None:
            self.state = start_state
            self.tape = tape
            self.head_position = 0
        else:
            self.tape = []
            self.state, self.tape, self.head_position = self.decode_state_godel(initial_godel, len(tape))

    def step(self):
        if self.state == self.accept_state or self.state == self.reject_state:
            return
        
        current_symbol = self.tape[self.head_position]
        
        if (self.state, current_symbol) in self.transitions:
            new_state, new_symbol, direction = self.transitions[(self.state, current_symbol)]
            
            self.tape[self.head_position] = new_symbol            
            self.state = new_state
            
            if direction == 'R':
                self.head_position += 1
            elif direction == 'L':
                self.head_position -= 1
            
            if self.head_position < 0:
                self.tape.insert(0, self.blank)
                self.head_position = 0
            elif self.head_position >= len(self.tape):
                self.tape.append(self.blank)
        else:
            self.state = self.reject_state
    
    def run(self):
        steps = 0
        while self.state != self.accept_state and self.state != self.reject_state:
            self.step()
            steps += 1
        return steps
    
    def __str__(self):
        return f'State: {self.state}, Tape: {"".join(self.tape)}, Head: {self.head_position}'
    
    def prime_generator():
        candidate = 2
        while True:
            is_prime = True
            for num in range(2, int(candidate ** 0.5) + 1):
                if candidate % num == 0:
                    is_prime = False
                    break
            if is_prime:
                yield candidate
            candidate += 1

    def encode_state_godel(self) -> int:
        state_index = self.states.index(self.state) + 1
        tape_symbols = [self.tape_alphabet.index(symbol) + 1 for symbol in self.tape]

        print(f"Encoding State Index: {state_index}")
        print(f"Encoding Tape Symbols: {tape_symbols}")
        print(f"Head Position: {self.head_position}")

        # Call TuringMachine.prime_generator directly
        primes = list(itertools.islice(TuringMachine.prime_generator(), len(tape_symbols) + 2))
        
        godel_number = primes[0] ** state_index
        for i, symbol in enumerate(tape_symbols):
            godel_number *= primes[i + 1] ** symbol
        godel_number *= primes[len(tape_symbols) + 1] ** (self.head_position + 1)
        
        print(f"Encoded Gödel-like Number: {godel_number}")
        return godel_number

    def decode_state_godel(self, godel_number: int, tape_length: int):
        print(f"Initial Gödel Number: {godel_number}")

        # Call TuringMachine.prime_generator directly for primes collection
        primes = list(itertools.islice(TuringMachine.prime_generator(), len(self.states) + len(self.tape_alphabet) + tape_length + 2))
        
        print(f"Generated Primes: {primes}")
        state_index = 0
        head_position = 0

        # Decode state
        for idx in range(1, len(self.states) + 1):
            if godel_number % primes[0] ** idx == 0:
                state_index = idx
            else:
                break
        godel_number //= primes[0] ** state_index

        # Decode head position
        for pos in range(1, tape_length + 1):
            if godel_number % primes[1] ** pos == 0:
                head_position = pos
            else:
                break
        godel_number //= primes[1] ** head_position
        head_position -= 1
        
        # Decode tape symbols
        tape_symbols = []
        for i in range(tape_length):
            symbol_idx = 0
            prime = primes[i + 2]
            print(f"Checking for symbol at tape index {i} using prime {prime}")

            for sym in range(1, len(self.tape_alphabet) + 1):
                if godel_number % prime ** sym == 0:
                    symbol_idx = sym
                else:
                    break
            
            if symbol_idx == 0:
                raise ValueError(f"Error decoding symbol, resulting in symbol_idx: {symbol_idx} for prime {prime}")
            godel_number //= prime ** symbol_idx
            tape_symbols.append(symbol_idx - 1)

        state = self.states[state_index - 1]
        tape = [self.tape_alphabet[i] for i in tape_symbols]

        print(f"Decoded Tape Symbols: {tape_symbols}, Tape: {tape}")
        print(f"Decoded State Index: {state_index}, Head Position: {head_position}")

        return state, tape, head_position
        
# Example usage
if __name__ == "__main__":
    states = ['q0', 'q1', 'qAccept', 'qReject']
    tape_alphabet = ['0', '1', '_']
    tape = ['1', '0', '1', '1', '_', '_']
    blank = '_'
    transitions = {
        ('q0', '1'): ('q1', '0', 'R'),
        ('q0', '0'): ('q0', '1', 'R'),
        ('q1', '1'): ('q0', '0', 'L'),
        ('q1', '0'): ('q1', '1', 'R'),
        ('q0', '_'): ('qAccept', '_', 'R'),
        ('qReject', '0'): ('qReject', '0', 'R'),  # Stay in reject state on 0
        ('qReject', '1'): ('qReject', '1', 'R'),  # Stay in reject state on 1
        ('qReject', '_'): ('qReject', '_', 'R')  # Stay in reject state on blank
    }
    start_state = 'q0'
    accept_state = 'qAccept'
    reject_state = 'qReject'

    initial_godel = None
    if len(sys.argv) > 1:
        initial_godel = int(sys.argv[1])

    tm = TuringMachine(states, tape_alphabet, tape, blank, transitions, start_state, accept_state, reject_state, initial_godel)
    steps = tm.run()
    print(f"Machine halted after {steps} steps.")
    print(tm)

    if initial_godel is None:
        # Print the initial encoded state only if not provided as an argument
        godel_number = tm.encode_state_godel()
        print(f"Encoded state (Gödel-like): {godel_number}")
