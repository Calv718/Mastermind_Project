"""
Below is the implementation of a Player class using the baseline strategy B1 from the Project Description:

B1: Exhaustively enumerate all possibilities. Guess each possibility in lexicographic order one at a time, and pay
no attention to the system’s responses. For example, if pegs p = 4 and colors c = 3, guess AAAA, AAAB, AAAC,
AABA, AABB, AABC and so on. This method will take at most c^p guesses.

"""

import time
import random
from player import *
from itertools import product


class Baseline1(Player):
    def __init__(self):

        super().__init__()
        self.player_name = "Baseline1"
        #Initialize data structure to store possibilities
        self.possible_codes = [] 

    def make_guess(self, board_length: int, colors: list[str], scsa_name: str, last_response: tuple[int, int, int]) -> str:
            # Initialize possibilities in lexicographic order
            if not self.possible_codes:
                self.possible_codes = [''.join(p) for p in product(colors, repeat=board_length)]

            elif self.possible_codes:
                #Grab a possibility and store it in guess
                guess = self.possible_codes.pop(0)

            else:
                #Make a random guess
                guess = ''.join(random.choices(colors, k=board_length))

            return guess