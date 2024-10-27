from player import *
from itertools import product
import random
import time

class B2_Player(Player):

    def __init__(self):

        super().__init__()
        self.player_name = "B2_Player"
        self.possible_codes = []  # List to keep track of all possible codes
        self.previous_guesses = []  # List to store previous guesses

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
            if time.time() - start_time > 4.8:
                # If we are nearing the time limit, make a quick random guess
                guess = ''.join(random.choices(colors, k=board_length))

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