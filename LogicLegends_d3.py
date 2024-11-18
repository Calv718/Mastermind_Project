'''
Below is the implementation of the tournament player from the Logic Legends.

Due to the success of the Baseline2 implementation, the decision was made to keep the majority of that implementation for Deadline3, with some modifications.
Depending on which SCSA is being used, there will be restrictions made to the list of all possible codes.
The function is_consistent_with_feedback is the same for this player as in Baseline2 
'''


import time
import random
from player import *
from itertools import product


class LogicLegends(Player):

    def __init__(self):
        """Constructor for LogicLegends"""

        super().__init__()
        self.player_name = "LogicLegends"
        self.possible_codes = []    # List to keep track of all possible codes
        self.previous_guesses = []  # List to store previous guesses
        self.time_cutoff = 5       
        self.time_buffer = 0.1  

    def make_guess(self, board_length: int, colors: list[str], scsa_name: str, last_response: tuple[int, int, int]) -> str:
        """Makes a guess of the secret code for Mastermind

        Args:
            board_length (int): Number of pegs of secret code.
            colors (list[str]]): All possible colors that can be used to generate a code.
            scsa_name (str): Name of SCSA used to generate secret code.
            last_response (tuple[int, int, int]): (First element in tuple is the number of pegs that match exactly with the secret
                                        code for the previous guess, the second element is the number of pegs that are
                                        the right color, but in the wrong location for the previous guess, and the third
                                        element is the number of guesses so far.)
        Returns:
            str: Returns guess
        """

        start_time = time.time()  # Start the timer

        # If this is the first guess, generate all possible codes
        if not self.possible_codes:
            # Uses the product function from itertools to generate the Cartesian product of iterable inputs, colors, for board_length times
            self.possible_codes = [''.join(p) for p in product(colors, repeat=board_length)]



        # Adapt strategy based on the SCSA used
        if scsa_name == "TwoColor":
            # Restricts guesses to codes with exactly 2 unique colors ("AB", "BA", "BC")
            self.possible_codes = [code for code in self.possible_codes if len(set(code)) == 2]
        
        elif scsa_name == "ABColor":
            # Restricts guesses to codes that only use the colors "A" and "B", ("AA", "AB", "BB")
            self.possible_codes = [code for code in self.possible_codes if set(code).issubset({"A", "B"})]
        
        elif scsa_name == "TwoColorAlternating":
            # Restricts guesses to codes that alternate between two colors ("ABAB" or "BABA")
            self.possible_codes = [code for code in self.possible_codes if self.is_alternating(code)]
        
        elif scsa_name == "OnlyOnce":
            # Restricts guesses to codes where each color appears at most once "ABCD"
            self.possible_codes = [code for code in self.possible_codes if len(set(code)) == len(code)]

        elif scsa_name == "FirstLast":
            # Restrict codes where the first and last colors must be the same
            self.possible_codes = [code for code in self.possible_codes if code[0] == code[-1]]
        
        # elif scsa_name == "UsuallyFewer":
        #     # Ensure that the code uses a relatively small number of colors depending on the probability
        #     probability = random.randint(0, 100)
        #     if probability < 90:
        #         # 90% chance that the number of colors used in the code will be kept to 2 or 3 colors max
        #         self.possible_codes = [code for code in self.possible_codes if len(set(code)) in [2, 3]] 
        #     else:
        #         # 10% chance that the number of colors used in the code will be more than 3
        #         self.possible_codes = [code for code in self.possible_codes if len(set(code)) > 3]
        
        # elif scsa_name == "PreferFewer":
        #     # Restricts guesses to codes that prefer 1, 2, or 3 unique colors.
        #     self.possible_codes = [code for code in self.possible_codes if len(set(code)) <= 3]
            
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
            # If we are nearing the time limit, use the last guess
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
        return (exact_matches, almost_matches, feedback[2]) == feedback

    def is_alternating(self, code: str) -> bool:
        """Check if the code follows an alternating color pattern (e.g., ABAB)"""
        return all(code[i] != code[i+1] for i in range(len(code) - 1))

