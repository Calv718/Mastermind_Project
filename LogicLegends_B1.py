"""
Below is the implementation of a Player class using the baseline strategy B1 from the Project Description:

B1: Exhaustively enumerate all possibilities. Guess each possibility in lexicographic order one at a time, and pay
no attention to the system's responses. For example, if pegs p = 4 and colors c = 3, guess AAAA, AAAB, AAAC,
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

            if self.possible_codes:
                #Grab a possibility and store it in guess
                guess = self.possible_codes.pop(0)

            else:
                #Make a random guess
                guess = ''.join(random.choices(colors, k=board_length))

            return guess
    


class Baseline2(Player):

    def __init__(self):

        super().__init__()
        self.player_name = "Baseline2"
        self.possible_codes = []  # List to keep track of all possible codes
        self.previous_guesses = []  # List to store previous guesses
        self.time_cutoff = 5       
        self.time_buffer = 0.1  

    def make_guess(self, board_length: int, colors: list[str], scsa_name: str, last_response: tuple[int, int, int]) -> str:
            start_time = time.time()  # Start the timer

            # If this is the first guess, generate all possible codes
            if not self.possible_codes:
                self.possible_codes = [''.join(p) for p in product(colors, repeat=board_length)]

            # If there was a previous guess, filter out inconsistent codes based on the feedback
            if self.previous_guesses:
                last_guess = self.previous_guesses[-1]
                self.possible_codes = [
                    code for code in self.possible_codes 
                    if self.is_consistent_with_feedback(last_guess, code, last_response)
                ]

            # Check if we are close to the time limit (5 seconds)
            elapsed_time = time.time() - start_time
            if elapsed_time > self.time_cutoff - self.time_buffer:
                # If we are nearing the time limit, use the last quess
                if self.previous_guesses:
                    guess = self.previous_guesses[-1]

            elif self.possible_codes:
                # Select the next guess from the filtered list of possible codes
                guess = self.possible_codes.pop(0)

            else:
                # Fallback: make a random guess if there are no possible codes left
                guess = ''.join(random.choices(colors, k=board_length))

            # Keep track of the current guess
            self.previous_guesses.append(guess)
            return guess

    def is_consistent_with_feedback(self, guess: str, code: str, feedback: tuple[int, int, int]) -> bool:

        # Peg number where BOTH the guess and the code have the same color in the same position
        exact_matches = sum(1 for g, c in zip(guess, code) if g == c)

        # Number of times each color appears in the guess
        guess_counts = {color: guess.count(color) for color in set(guess)}

        # Number of times each color appears in the hidden code
        code_counts = {color: code.count(color) for color in set(code)}

        # Sums the minimum frequencies of each color in both the guess and hidden code -> subtracting the exact_matches
        almost_matches = sum(min(guess_counts.get(color, 0), code_counts.get(color, 0)) for color in set(guess)) - exact_matches

        # Compare calculated feedback with the provided feedback
        # True -> calculated (exact_matches, almost_matches, feedback[2]) == given feedback tuple
        return (exact_matches, almost_matches, feedback[2]) == feedback



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
