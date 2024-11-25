'''
Below is the near final Player for the Mastermind Project from the Logic Legends team.

It build off the implementation for deadline 2 and continues with:
 - reducing the search space with filters specific to each SCSA
 - using the feedback to determine what steps to take next
 - has a simple heursitic to minimize the solution space.
'''


import time
import random
from player import *
from itertools import product, combinations
from collections import Counter


class LogicLegends(Player):
    def __init__(self):
        super().__init__()
        self.player_name = "LogicLegends"
        self.possible_codes = []  # List to keep track of all possible codes
        self.previous_guesses = []  # List to store previous guesses
        self.time_cutoff = 3  # Per-round time limit in seconds
        self.time_buffer = 0.4  # Buffer to prevent exceeding time limit
        self.max_guesses_per_round = 100  # Maximum guesses allowed per round

    def make_guess(self, board_length: int, colors: list[str], scsa_name: str, last_response: tuple[int, int, int]) -> str:
        start_time = time.time()  # Start the timer

        # Initialize possible codes only once per round
        if not self.possible_codes:
            self.possible_codes = self.generate_possible_codes(scsa_name, board_length, colors)

        # Filter codes based on the feedback from the last guess
        if self.previous_guesses and last_response != (0, 0, 0):
            last_guess = self.previous_guesses[-1]
            self.possible_codes = [
                code for code in self.possible_codes
                if self.is_consistent_with_feedback(last_guess, code, last_response)
            ]

        # Decide on the next guess based on the current search space
        if len(self.possible_codes) > 500_000:
            guess = self.heuristic_guess()
        elif self.possible_codes:
            guess = self.possible_codes.pop(0)  # Take the first possible code
        else:
            # If no possible codes remain, fallback to a safe random guess
            guess = self.generate_fallback_guess(scsa_name, board_length, colors)

        # Ensure that the guess is legal before returning
        if not self.is_guess_legal(guess, board_length, colors):
            # If the guess is illegal, attempt to make a legal fallback guess
            guess = self.generate_fallback_guess(scsa_name, board_length, colors)

        # Check if nearing time limit and adjust if necessary
        elapsed_time = time.time() - start_time
        if elapsed_time > self.time_cutoff - self.time_buffer and self.previous_guesses:
            # Reuse the last guess to save time
            guess = self.previous_guesses[-1]

        # Store the current guess and return
        self.previous_guesses.append(guess)
        return guess

    def generate_possible_codes(self, scsa_name: str, length: int, colors: list[str]) -> list[str]:
        """
        Generate all possible codes based on the selected SCSA.
        """
        generator_method = getattr(self, f'generate_{scsa_name.lower()}', None)
        if generator_method:
            return generator_method(length, colors)
        else:
            raise ValueError(f"Unsupported SCSA: {scsa_name}")

    def generate_insertcolors(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: InsertColors - Generates codes by selecting colors at random.
        """
        # Use list comprehension for efficient generation
        # return [''.join(p) for p in product(colors, repeat=length)]

        # print('starting to generate all codes')
        
        # all_combinations = [''.join(p) for p in product(colors, repeat=length)]    
        # # print("done generating all codes, now focus on reducing to 10%")
        
        # num_combinations_to_select = len(all_combinations) // 1000
        # # print("done reducing, now return random sample")
    
        # return random.sample(all_combinations, num_combinations_to_select)




        total_combinations = len(list(combinations(colors, length)))

        # Calculate the number of combinations to select (1/1000 of all combinations)
        num_combinations_to_select = total_combinations

        # Generate 1/1000 of the combinations randomly
        sampled_combinations = []
        for _ in range(num_combinations_to_select):
                random_combination = random.sample(list(combinations(colors, length)), 1)
                sampled_combinations.append(random_combination[0])
        
        # Print the sampled combinations
        return(sampled_combinations)
    

    def generate_twocolor(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: TwoColor - Generates codes containing exactly two distinct colors,
                        ensuring both are used at least once.
        """
        codes = []
        # Generate all combinations of two distinct colors
        for color1, color2 in combinations(colors, 2):
            # Generate all possible codes with these two colors
            for p in product([color1, color2], repeat=length):
                code = ''.join(p)
                if color1 in code and color2 in code:
                    codes.append(code)
        return codes

    def generate_abcolor(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: ABColor - Generates codes containing only "A" and "B", ensuring both are present.
        """
        # Ensure 'A' and 'B' are in the colors list
        if 'A' not in colors or 'B' not in colors:
            return []
        return self.generate_twocolor(length, ['A', 'B'])

    def generate_twocoloralternating(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: TwoColorAlternating - Generates codes that alternate between two distinct colors.
        """
        codes = []
        # Generate all combinations of two distinct colors
        for color1, color2 in combinations(colors, 2):
            # Generate two possible alternating patterns for each color pair
            pattern1 = ''.join([color1 if i % 2 == 0 else color2 for i in range(length)])
            pattern2 = ''.join([color2 if i % 2 == 0 else color1 for i in range(length)])
            codes.extend([pattern1, pattern2])
        return codes

    def generate_onlyonce(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: OnlyOnce - Generates codes where each color appears at most once.
        If length > number of colors, the excess positions can have any color from the list.
        """
        codes = []
        if length <= len(colors):
            # All colors in the code must be unique
            for p in combinations(colors, length):
                codes.append(''.join(p))
        else:
            # First len(colors) positions have unique colors
            # Remaining positions can have any color (allowing repetitions)
            unique_part_length = len(colors)
            unique_codes = [''.join(p) for p in combinations(colors, unique_part_length)]
            remaining_length = length - unique_part_length
            for unique_code in unique_codes:
                for extra in product(colors, repeat=remaining_length):
                    full_code = unique_code + ''.join(extra)
                    codes.append(full_code)
        return codes

    def generate_firstlast(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: FirstLast - Generates codes where the first and last colors are identical.
        """
        codes = []
        if length < 2:
            # Not enough positions to have first and last
            return []
        for color in colors:
            if length == 2:
                # Only first and last colors
                codes.append(color * 2)
            else:
                # Middle positions can have any colors
                for middle in product(colors, repeat=length - 2):
                    code = color + ''.join(middle) + color
                    codes.append(code)
        return codes

    def generate_usuallyfewer(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: UsuallyFewer - Generates codes that usually have fewer (2 or 3) colors,
                           with a small probability of using all available colors.
        """
        codes = []
        # 90% use 2 or 3 distinct colors
        for k in [2, 3]:
            for subset in combinations(colors, k):
                for p in product(subset, repeat=length):
                    codes.append(''.join(p))
        # 10% use all available colors
        for p in product(colors, repeat=length):
            codes.append(''.join(p))
        return codes

    def generate_preferfewer(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: PreferFewer - Generates codes with a preference for fewer colors based on a specific probability distribution.
        """
        codes = []
        # 49% use 1 distinct color
        for subset in combinations(colors, 1):
            for p in product(subset, repeat=length):
                codes.append(''.join(p))
        # 25% use 2 distinct colors
        for subset in combinations(colors, 2):
            for p in product(subset, repeat=length):
                codes.append(''.join(p))
        # 13% use 3 distinct colors
        for subset in combinations(colors, 3):
            for p in product(subset, repeat=length):
                codes.append(''.join(p))
        # 12% use 4 distinct colors
        for subset in combinations(colors, 4):
            for p in product(subset, repeat=length):
                codes.append(''.join(p))
        # 3% use 5 distinct colors
        if len(colors) >= 5:
            for subset in combinations(colors, 5):
                for p in product(subset, repeat=length):
                    codes.append(''.join(p))
        # 2% use all available colors
        for p in product(colors, repeat=length):
            codes.append(''.join(p))
        return codes

    def generate_fallback_guess(self, scsa_name: str, length: int, colors: list[str]) -> str:
        """
        Generate a fallback guess based on the SCSA constraints when possible_codes is empty.
        """
        generator_method = getattr(self, f'generate_{scsa_name.lower()}', None)
        if generator_method:
            # Generate a single random code from the SCSA
            possible_codes = generator_method(length, colors)
            if possible_codes:
                return random.choice(possible_codes)
        # If SCSA is unsupported or no codes are generated, fallback to a safe guess
        return ''.join(random.choices(colors, k=length))
        
    
        # # Choose the first color repeated, which is guaranteed to be legal
        # if colors:
        #     return colors[0] * length
        # else:
        #     # As a last resort, return a default string of 'A's
        #     return 'A' * length

    def heuristic_guess(self) -> str:
        """
        Select the next guess using a heuristic to minimize the solution space.
        """
        # Scoring function for guesses
        def score_guess(guess):
            feedback_distribution = Counter(
                self.simulate_feedback(guess, code) for code in self.possible_codes
            )
            # Minimize the largest partition size of feedback groups
            return max(feedback_distribution.values())

        # Evaluate all remaining possible codes as candidates
        # To optimize, sample a subset if possible_codes is still very large
        if len(self.possible_codes) > 1000:
            sampled_codes = random.sample(self.possible_codes, 1000)
        else:
            sampled_codes = self.possible_codes

        # Find the guess with the minimum maximum partition size
        best_guess = min(sampled_codes, key=score_guess)
        return best_guess

    def simulate_feedback(self, guess: str, code: str) -> tuple[int, int]:
        """
        Simulate feedback for a given guess against a code.
        Returns (exact_matches, almost_matches).
        """
        exact_matches = sum(1 for g, c in zip(guess, code) if g == c)
        guess_counts = Counter(guess)
        code_counts = Counter(code)
        almost_matches = sum(min(guess_counts[color], code_counts[color]) for color in guess_counts) - exact_matches
        return exact_matches, almost_matches

    def is_consistent_with_feedback(self, guess: str, code: str, feedback: tuple[int, int, int]) -> bool:
        """
        Check if a given code is consistent with the feedback from a previous guess.
        """
        exact_matches, almost_matches = self.simulate_feedback(guess, code)
        # Compare only exact and almost matches
        return (exact_matches, almost_matches) == feedback[:2]

    def is_guess_legal(self, guess: str, board_length: int, colors: list[str]) -> bool:
        """
        Verify that the guess is legal:
        - Correct number of pegs
        - All colors are within the allowed color set
        """
        if len(guess) != board_length:
            return False
        for peg in guess:
            if peg not in colors:
                return False
        return True

    def reset_for_new_round(self):
        """
        Reset the player's state for a new round.
        """
        self.possible_codes = []
        self.previous_guesses = []


    def generate_mystery1(self, length: int, colors: list[str]) -> list[str]:
        """
        Used to generate the possible codes for mystery1 SCSA
        """
        
        return [''.join(p) for p in product(colors, repeat=length)]
    
    def generate_mystery2(self, length: int, colors: list[str]) -> list[str]:
        """
        Used to generate the possible codes for mystery1 SCSA
        """
        
        return [''.join(p) for p in product(colors, repeat=length)]
    
    def generate_mystery3(self, length: int, colors: list[str]) -> list[str]:
        """
        Used to generate the possible codes for mystery1 SCSA
        """
        
        return [''.join(p) for p in product(colors, repeat=length)]
    
    def generate_mystery4(self, length: int, colors: list[str]) -> list[str]:
        """
        Used to generate the possible codes for mystery1 SCSA
        """
        
        return [''.join(p) for p in product(colors, repeat=length)]
    
    def generate_mystery5(self, length: int, colors: list[str]) -> list[str]:
        """
        Used to generate the possible codes for mystery1 SCSA
        """
        
        return [''.join(p) for p in product(colors, repeat=length)]

    def generate_mystery6(self, length: int, colors: list[str]) -> list[str]:
        """
        Used to generate the possible codes for mystery1 SCSA
        """
        
        return [''.join(p) for p in product(colors, repeat=length)]

    def generate_mystery7(self, length: int, colors: list[str]) -> list[str]:
        """
        Used to generate the possible codes for mystery1 SCSA
        """
        
        return [''.join(p) for p in product(colors, repeat=length)]

    