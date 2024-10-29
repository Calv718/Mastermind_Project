"""
Below is the implementation of a Player class using the baseline strategy B3 from the Project Description:

B3: Make your first c - 1 guesses monochromatic: "all A's," "all B's,"… for all but one of the c colors. That will
tell you how many pegs of each color are in the answer. (You don't need to actually guess the last color; you can
compute how many of those there are from the other answers.) Then you generate and test only answers consistent
with that known color distribution.

"""

import time
import random
from player import *
from itertools import product

class Baseline3(Player):

    def __init__(self):
        super().__init__()
        self.player_name = "Baseline3"
        self.possible_codes = []        # Potential valid guesses based on identified patterns
        self.color_counts = {}          # Dict to track frequencies of each color
        self.previous_guesses = []      # List to store all previous guesses made
        self.pattern_index = 0          # Index to keep track of which color is being tested
        self.step = 0                   # Step counter for the number of guesses made
        self.identified_colors = []     # List to store identified colors that are in the code
        self.scsa_name = None           # To store the current SCSA being used
        self.time_cutoff = 5       
        self.time_buffer = 0.1  

    def make_guess(self, board_length: int, colors: list[str], scsa_name: str, last_response: tuple[int, int, int]) -> str:
        start_time = time.time()    # Start the timer

        # Set the SCSA name on the first guess
        if self.scsa_name is None:
            self.scsa_name = scsa_name

        # Handle feedback from the last guess if we are past the first step
        if self.step > 0:
            exact_matches, almost_matches, _ = last_response

            # If the response indicates any correct or almost correct pegs, update identified colors
            if self.step <= len(colors) and (exact_matches + almost_matches) > 0:
                identified_color = colors[self.pattern_index - 1]
                if identified_color not in self.identified_colors:
                    self.identified_colors.append(identified_color)

        # Check if we are close to the time limit (5 seconds)
        elapsed_time = time.time() - start_time
        if elapsed_time > self.time_cutoff - self.time_buffer:
            # Make a random fallback guess if time is running out
            guess = ''.join(random.choices(colors, k=board_length))
            
        else:
            # Adapt strategy based on identified patterns and SCSA characteristics
            guess = self.adapt_strategy(board_length, colors)

        # Store the current guess in the list of previous guesses
        self.previous_guesses.append(guess)
        self.step += 1      # Increment the step count
        return guess

    def adapt_strategy(self, board_length: int, colors: list[str]) -> str:

        # If fewer than 2 colors are identified, continue making monochromatic guesses
        if len(self.identified_colors) < 2 and self.pattern_index < len(colors):
            current_color = colors[self.pattern_index]
            guess = current_color * board_length
            self.pattern_index += 1  # Move to the next color

        elif len(self.identified_colors) >= 2:
            # If two or more colors are identified, generate guesses based on likely SCSA patterns
            if not self.possible_codes:

                # Generate different code patterns based on common SCSA characteristics
                if self.scsa_name in ["TwoColor", "ABColor", "TwoColorAlternating"]:
                    self.possible_codes = self.generate_TwoColor(board_length, self.identified_colors)
                
                elif self.scsa_name in ["FirstLast"]:
                    self.possible_codes = self.generate_FirstLast(board_length, self.identified_colors, colors)
                
                elif self.scsa_name in ["OnlyOnce"]:
                    self.possible_codes = self.generate_OnlyOnce(board_length, self.identified_colors, colors)
                
                elif self.scsa_name in ["UsuallyFewer", "PreferFewer", "InsertColors"]:
                    self.possible_codes = self.generate_PreferredColors(board_length, self.identified_colors, colors)
                
                else:
                    # Unknown SCSA - fall back to a general approach
                    self.possible_codes = self.generate_TwoColor(board_length, self.identified_colors)

            # Make a guess from the list of possible combinations
            guess = self.possible_codes.pop(0) if self.possible_codes else ''.join(random.choices(colors, k=board_length))
       
        else:
            # If no colors are identified yet, use the first color for the entire code
            guess = colors[0] * board_length

        return guess

    def generate_TwoColor(self, board_length: int, identified_colors: list[str]) -> list[str]:

        # Generate all combinations of the two identified colors
        return [''.join(p) for p in product(identified_colors, repeat=board_length)]

    def generate_FirstLast(self, board_length: int, identified_colors: list[str], colors: list[str]) -> list[str]:
        # Generate combinations where the first and last colors are the same

        valid_codes = []

        for color in identified_colors:
            middle_combinations = product(colors, repeat=board_length - 2)
            for mid in middle_combinations:
                code = color + ''.join(mid) + color
                valid_codes.append(code)

        return valid_codes

    def generate_OnlyOnce(self, board_length: int, identified_colors: list[str], colors: list[str]) -> list[str]:
        from itertools import permutations

        # Generate combinations where each color appears at most once
        return [''.join(p) for p in permutations(identified_colors, board_length)]

    def generate_PreferredColors(self, board_length: int, identified_colors: list[str], colors: list[str]) -> list[str]:
        # Generate combinations with fewer colors or random selection

        possible_codes = []

        for _ in range(100):  # Generate a fixed number of combinations
            num_colors = random.randint(1, min(3, len(identified_colors)))
            selected_colors = random.sample(identified_colors, k=num_colors)
            possible_codes.append(''.join(random.choices(selected_colors, k=board_length)))

        return possible_codes
