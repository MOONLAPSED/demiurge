import itertools
import logging
from typing import List, Tuple, Dict
from decimal import Decimal, getcontext

# Use Decimal with a higher precision for large numbers if needed
getcontext().prec = 100

# Set up logging with UTF-8 encoding for broader character support
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('turing_machine.log', mode='w', encoding='utf-8')
    ]
)

logger = logging.getLogger('TuringMachine')

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
        logger.info("Initializing Turing Machine")
        
        self.states = states
        self.tape_alphabet = tape_alphabet
        self.blank = blank
        self.transitions = transitions
        self.accept_state = accept_state
        self.reject_state = reject_state

        if initial_godel is not None:
            logger.info(f"Initializing from Gödel number: {initial_godel}")
            self.state, self.tape, self.head_position = self.decode_state_godel(initial_godel, len(tape))
        else:
            logger.info("Initializing from direct values")
            self.state = start_state
            self.tape = tape.copy()
            self.head_position = 0
        
        logger.info(f"Initial configuration: {self}")

    def decode_state_godel(self, godel_number: int, tape_length: int):
        logger.info(f"Decoding Gödel number: {godel_number}")
        number = Decimal(godel_number)

        primes = list(itertools.islice(self.prime_generator(), tape_length + 2))
        
        # Decode head position
        head_position = 0
        last_prime = primes[-1]
        while number % last_prime == 0:
            number /= last_prime
            head_position += 1
            logger.debug(f"Decoded head position factor: {head_position}, Remaining number: {number}")
        head_position -= 1

        # Decode state
        state_index = 0
        first_prime = primes[0]
        while number % first_prime == 0:
            number /= first_prime
            state_index += 1
            logger.debug(f"Decoded state factor: {state_index}, Remaining number: {number}")
        state_index -= 1
        state = self.states[state_index] if state_index >= 0 and state_index < len(self.states) else 'INVALID'

        # Decode tape
        tape = []
        for i in range(tape_length):
            symbol_index = 0
            prime = primes[i + 1]
            while number % prime == 0:
                number /= prime
                symbol_index += 1
                logger.debug(f"Decoded symbol factor for position {i}: {symbol_index}, Remaining number: {number}")
            
            tape.append(self.tape_alphabet[symbol_index - 1] if symbol_index > 0 else self.blank)

        logger.info(f"Decoded configuration: State: {state}, Tape: '{''.join(tape)}', Head: {head_position}")
        return state, tape, head_position

    def step(self):
        if self.state in [self.accept_state, self.reject_state]:
            logger.debug(f"Machine in halting state: {self.state}")
            return
        
        current_symbol = self.tape[self.head_position]
        logger.debug(f"State: {self.state}, Symbol: {current_symbol}, Position: {self.head_position}")
        
        transition_key = (self.state, current_symbol)
        if transition_key in self.transitions:
            new_state, new_symbol, direction = self.transitions[transition_key]
            logger.debug(f"Transition: {transition_key} -> ({new_state}, {new_symbol}, {direction})")
            
            self.tape[self.head_position] = new_symbol
            self.state = new_state
            self.move_head(direction)
        else:
            logger.warning(f"No transition for {transition_key}")
            self.state = self.reject_state
        
        logger.debug(f"New configuration: {self}")

    def move_head(self, direction: str):
        if direction == 'R':
            self.head_position += 1
            if self.head_position >= len(self.tape):
                logger.debug("Extending tape right")
                self.tape.append(self.blank)
        elif direction == 'L':
            self.head_position -= 1
            if self.head_position < 0:
                logger.debug("Extending tape left")
                self.tape.insert(0, self.blank)
                self.head_position = 0

    def encode_state_godel(self) -> Decimal:
        logger.info("Encoding machine state to Gödel number")
        state_index = self.states.index(self.state) + 1
        tape_indices = [self.tape_alphabet.index(symbol) + 1 for symbol in self.tape]
        head_adjusted = self.head_position + 1 

        primes = list(itertools.islice(self.prime_generator(), len(tape_indices) + 2))
        godel_number = Decimal(primes[0] ** state_index) * Decimal(primes[-1] ** head_adjusted)

        for i, symbol_index in enumerate(tape_indices):
            godel_number *= Decimal(primes[i + 1] ** symbol_index)
        
        logger.debug(f"Encoded Gödel number: {godel_number}")
        return godel_number

    def prime_generator(self):
        n = 2
        while True:
            if all(n % i != 0 for i in range(2, int(n ** 0.5) + 1)):
                yield n
            n += 1

    def run(self):
        logger.info("Running Turing Machine")
        steps = 0
        while self.state not in [self.accept_state, self.reject_state]:
            self.step()
            steps += 1
        logger.info(f"Machine halted after {steps} steps in state {self.state}")
        return steps

    def __str__(self):
        tape_str = ''.join(self.tape).replace(' ', '_')
        return f'State: {self.state}, Tape: {tape_str}, Head: {self.head_position}'

if __name__ == "__main__":
    logger.info("Starting Turing Machine program")
    
    states = ['q0', 'q1', 'qAccept', 'qReject']
    tape_alphabet = ['0', '1', '_']
    tape = ['1', '0', '1', '_']
    blank = '_'
    """infinite_loop
        transitions = {
            ('q0', '1'): ('q1', '0', 'R'),
            ('q0', '0'): ('q0', '1', 'R'),
            ('q1', '1'): ('q0', '0', 'L'),
            ('q1', '0'): ('q1', '1', 'R'),
        ('q0', '_'): ('qAccept', '_', 'R'),
        ('q1', '_'): ('q1', '_', 'R'),  # New transition for thawing
        }
    """
    transitions = {
        ('q0', '1'): ('q1', '0', 'R'),
        ('q0', '0'): ('q0', '1', 'R'),
        ('q1', '1'): ('q0', '0', 'L'),
        ('q1', '0'): ('q1', '1', 'R'),
        ('q0', '_'): ('qAccept', '_', 'R'),
        ('q1', '_'): ('qReject', '_', 'R'),  # Changed to allow exiting loop
    }
    start_state = 'q0'
    accept_state = 'qAccept'
    reject_state = 'qReject'

    initial_godel = None
    tm = TuringMachine(states, tape_alphabet, tape, blank, transitions, 
                      start_state, accept_state, reject_state, initial_godel)
    steps = tm.run()
    logger.info(f"Machine completed in {steps} steps")
    final_godel = tm.encode_state_godel()
    logger.info(f"Final state Gödel number: {final_godel}")