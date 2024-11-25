import time
import random
from player import Player
from itertools import product, combinations
from collections import Counter


class LogicLegends(Player):
    """
    LogicLegends is a player that uses logical strategies to make guesses in the game.
    It maintains a list of possible codes and refines them based on feedback from previous guesses.
    """

    def __init__(self):
        """
        Initialize the LogicLegends player with default settings.
        """
        super().__init__()
        self.player_name = "LogicLegends"
        self.possible_codes = []  # List to keep track of all possible codes
        self.previous_guesses = []  # List to store previous guesses
        self.time_cutoff = 5  # Per-round time limit in seconds
        self.time_buffer = 0.1  # Buffer to prevent exceeding time limit
        self.max_guesses_per_round = 100  # Maximum guesses allowed per round

    def make_guess(self, board_length: int, colors: list[str], scsa_name: str,
                  last_response: tuple[int, int, int]) -> str:
        """
        Make a guess based on the current state of the game.

        Args:
            board_length (int): The length of the code to guess.
            colors (list[str]): The list of available colors.
            scsa_name (str): The name of the Selected Code Space Algorithm (SCSA).
            last_response (tuple[int, int, int]): Feedback from the last guess.

        Returns:
            str: The next guess.
        """
        start_time = time.time()  # Start the timer

        # Initialize possible codes only once per round
        if not self.possible_codes:
            self.possible_codes = self.generate_possible_codes(scsa_name, board_length, colors)

        # Filter codes based on the feedback from the last guess
        if self.previous_guesses and last_response != (0, 0, 0):
            last_guess = self.previous_guesses[-1]
            self.filter_possible_codes(last_guess, last_response)

        # Decide on the next guess based on the current search space
        guess = self.select_next_guess(scsa_name, board_length, colors)

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

        Args:
            scsa_name (str): The name of the Selected Code Space Algorithm (SCSA).
            length (int): The length of the code to generate.
            colors (list[str]): The list of available colors.

        Returns:
            list[str]: A list of possible codes.
        """
        # Dynamically retrieve the generator method based on SCSA name
        generator_method = getattr(self, f'generate_{scsa_name}', None)
        if generator_method:
            return generator_method(length, colors)

    def filter_possible_codes(self, last_guess: str, feedback: tuple[int, int, int]):
        """
        Filter the possible codes based on the feedback from the last guess.

        Args:
            last_guess (str): The last guess made.
            feedback (tuple[int, int, int]): Feedback from the last guess.
        """
        # Retain only those codes that are consistent with the feedback
        self.possible_codes = [
            code for code in self.possible_codes
            if self.is_consistent_with_feedback(last_guess, code, feedback)
        ]

    def select_next_guess(self, scsa_name: str, length: int, colors: list[str]) -> str:
        """
        Select the next guess based on the current possible codes.

        Args:
            scsa_name (str): The name of the Selected Code Space Algorithm (SCSA).
            length (int): The length of the code to guess.
            colors (list[str]): The list of available colors.

        Returns:
            str: The selected next guess.
        """
        # If the search space is too large, use a heuristic to choose the guess
        if len(self.possible_codes) > 500_000:
            return self.heuristic_guess()
        elif self.possible_codes:
            return self.possible_codes.pop(0)  # Take the first possible code
        else:
            # If no possible codes remain, fallback to a safe random guess
            return self.generate_fallback_guess(scsa_name, length, colors)

    def is_consistent_with_feedback(self, guess: str, code: str, feedback: tuple[int, int, int]) -> bool:
        """
        Check if a given code is consistent with the feedback from a previous guess.

        Args:
            guess (str): The previous guess.
            code (str): The code to check.
            feedback (tuple[int, int, int]): Feedback from the previous guess.

        Returns:
            bool: True if consistent, False otherwise.
        """
        # Simulate feedback for the guess against the code
        exact_matches, almost_matches = self.simulate_feedback(guess, code)
        # Compare only exact and almost matches
        return (exact_matches, almost_matches) == feedback[:2]

    def is_guess_legal(self, guess: str, board_length: int, colors: list[str]) -> bool:
        """
        Verify that the guess is legal:
        - Correct number of pegs
        - All colors are within the allowed color set

        Args:
            guess (str): The guess to verify.
            board_length (int): The required length of the guess.
            colors (list[str]): The list of allowed colors.

        Returns:
            bool: True if the guess is legal, False otherwise.
        """
        # Check if the guess has the correct length
        if len(guess) != board_length:
            return False
        # Check if all pegs in the guess are valid colors
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

    def generate_fallback_guess(self, scsa_name: str, length: int, colors: list[str]) -> str:
        """
        Generate a fallback guess based on the SCSA constraints when possible_codes is empty.
        Ensures that the fallback guess is legal.

        Args:
            scsa_name (str): The name of the Selected Code Space Algorithm (SCSA).
            length (int): The length of the code to guess.
            colors (list[str]): The list of available colors.

        Returns:
            str: A fallback guess.
        """
        # Attempt to generate a code using the specified SCSA
        generator_method = getattr(self, f'generate_{scsa_name}', None)
        if generator_method:
            possible_codes = generator_method(length, colors)
            if possible_codes:
                return random.choice(possible_codes)
        # If SCSA is unsupported or no codes are generated, fallback to a safe guess
        if colors:
            return colors[0] * length  # Choose the first color repeated
        else:
            # As a last resort, return a default string of 'A's
            return 'A' * length

    def heuristic_guess(self) -> str:
        """
        Select the next guess using a heuristic to minimize the solution space.

        Returns:
            str: The heuristic-based guess.
        """
        def score_guess(guess):
            """
            Score a guess based on the distribution of possible feedbacks.
            The goal is to minimize the maximum size of any feedback group.

            Args:
                guess (str): The guess to score.

            Returns:
                int: The maximum size of any feedback group.
            """
            # Count how many codes would result in each type of feedback
            feedback_distribution = Counter(
                self.simulate_feedback(guess, code) for code in self.possible_codes
            )
            # Return the size of the largest feedback group
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

        Args:
            guess (str): The guess to simulate.
            code (str): The actual code.

        Returns:
            tuple[int, int]: A tuple containing the number of exact and almost matches.
        """
        # Count exact matches where both color and position are correct
        exact_matches = sum(1 for g, c in zip(guess, code) if g == c)
        # Count occurrences of each color in guess and code
        guess_counts = Counter(guess)
        code_counts = Counter(code)
        # Calculate almost matches by summing the minimum occurrences of each color
        almost_matches = sum(min(guess_counts[color], code_counts[color]) for color in guess_counts) - exact_matches
        return exact_matches, almost_matches

    # ---------------------- SCSA-Specific Methods ----------------------

    def generate_InsertColors(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: InsertColors - Generates codes by selecting colors at random.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of available colors.

        Returns:
            list[str]: A list of generated codes.
        """
        # Use list comprehension for efficient generation of all possible combinations
        return [''.join(p) for p in product(colors, repeat=length)]

    def generate_TwoColor(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: TwoColor - Generates codes containing exactly two distinct colors,
                        ensuring both are used at least once.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of available colors.

        Returns:
            list[str]: A list of generated codes.
        """
        codes = []
        # Generate all combinations of two distinct colors
        for color1, color2 in combinations(colors, 2):
            # Generate all possible codes with these two colors
            for p in product([color1, color2], repeat=length):
                code = ''.join(p)
                # Ensure both colors are present in the code
                if color1 in code and color2 in code:
                    codes.append(code)
        return codes

    def generate_ABColor(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: ABColor - Generates codes containing only "A" and "B", ensuring both are present.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of available colors.

        Returns:
            list[str]: A list of generated codes.
        """
        # Ensure 'A' and 'B' are in the colors list
        if 'A' not in colors or 'B' not in colors:
            return []
        # Reuse the TwoColor generator with only 'A' and 'B'
        return self.generate_TwoColor(length, ['A', 'B'])

    def generate_TwoColorAlternating(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: TwoColorAlternating - Generates codes that alternate between two distinct colors.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of available colors.

        Returns:
            list[str]: A list of generated codes.
        """
        codes = []
        # Generate all combinations of two distinct colors
        for color1, color2 in combinations(colors, 2):
            # Generate two possible alternating patterns for each color pair
            pattern1 = ''.join([color1 if i % 2 == 0 else color2 for i in range(length)])
            pattern2 = ''.join([color2 if i % 2 == 0 else color1 for i in range(length)])
            codes.extend([pattern1, pattern2])
        return codes

    def generate_OnlyOnce(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: OnlyOnce - Generates codes where each color appears at most once.
        If length > number of colors, the excess positions can have any color from the list.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of available colors.

        Returns:
            list[str]: A list of generated codes.
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

    def generate_FirstLast(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: FirstLast - Generates codes where the first and last colors are identical.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of available colors.

        Returns:
            list[str]: A list of generated codes.
        """
        codes = []
        if length < 2:
            # Cannot have first and last colors identical if length is less than 2
            return []

        max_total_codes = 500_000  # Maximum total codes to prevent excessive memory usage
        max_codes_per_color = 1000  # Maximum codes per color

        for color in colors:
            if len(codes) >= max_total_codes:
                break  # Stop if maximum total codes reached
            if length == 2:
                # If length is 2, the code is simply the color repeated
                codes.append(color * 2)
                continue

            # Calculate the total possible combinations for the middle positions
            total_possible = len(colors) ** (length - 2)
            if total_possible <= max_codes_per_color:
                # Generate all possible codes with the current color as first and last
                for middle in product(colors, repeat=length - 2):
                    code = color + ''.join(middle) + color
                    codes.append(code)
                    if len(codes) >= max_total_codes:
                        break
            else:
                # Sample a limited number of codes to avoid excessive memory usage
                sampled = set()
                while len(sampled) < max_codes_per_color:
                    middle = ''.join(random.choices(colors, k=length - 2))
                    sampled.add(middle)
                    if len(sampled) >= total_possible:
                        break  # All possible codes have been sampled
                for middle in sampled:
                    code = color + middle + color
                    codes.append(code)
                    if len(codes) >= max_total_codes:
                        break

        # Return only up to the maximum total codes
        return codes[:max_total_codes]

    def generate_UsuallyFewer(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: UsuallyFewer - Generates codes that usually have fewer (2 or 3) colors,
                           with a small probability of using all available colors.
        Improved to handle larger sizes by adding constraints to limit the search space.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of available colors.

        Returns:
            list[str]: A list of generated codes.
        """
        codes = []
        max_total = 500_000  # Maximum total codes to prevent excessive memory usage
        max_subset = 1000  # Maximum codes per color subset
        # Define the distribution: (number of colors, percentage probability)
        distribution = [(2, 36), (3, 54), (len(colors), 10)]  # 36% for 2, 54% for 3, 10% all colors

        for num_colors, prob in distribution:
            if num_colors > len(colors):
                continue  # Skip if the number of colors exceeds available colors
            # Generate all possible subsets of the specified number of colors
            subsets = list(combinations(colors, num_colors))
            random.shuffle(subsets)  # Shuffle to ensure random subsets are processed first
            # Calculate how many codes to generate per subset based on probability
            codes_per_subset = min(int(prob / 100 * max_total / len(distribution)), max_subset)

            for subset in subsets:
                # Calculate the total possible combinations for the subset
                total_possible = len(subset) ** length
                if total_possible <= codes_per_subset:
                    # Generate all possible codes for the subset
                    for p in product(subset, repeat=length):
                        codes.append(''.join(p))
                        if len(codes) >= max_total:
                            return codes
                else:
                    # Randomly sample codes to limit the number
                    sampled = set()
                    while len(sampled) < codes_per_subset and len(sampled) < total_possible:
                        code = ''.join(random.choices(subset, k=length))
                        sampled.add(code)
                    codes.extend(sampled)
                    if len(codes) >= max_total:
                        return codes[:max_total]
        return codes[:max_total]

    def generate_PreferFewer(self, length: int, colors: list[str]) -> list[str]:
        """
        SCSA: PreferFewer - Generates codes with a preference for fewer colors based on a specific probability distribution.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of available colors.

        Returns:
            list[str]: A list of generated codes.
        """
        codes = []
        max_total_codes = 500_000  # Maximum total codes to prevent excessive memory usage
        max_codes_per_subset = 1000  # Maximum codes per color subset

        # Define the probability distribution for distinct color counts
        distribution = [
            (1, 49),  # 49% probability for using 1 color
            (2, 25),  # 25% for 2 colors
            (3, 13),  # 13% for 3 colors
            (4, 12),  # 12% for 4 colors
            (5, 3)    # 3% for 5 colors
        ]

        for num_colors, prob in distribution:
            if num_colors > len(colors):
                continue  # Skip if the number of colors exceeds available colors

            # Generate all possible subsets of the specified number of colors
            subsets = list(combinations(colors, num_colors))
            random.shuffle(subsets)  # Shuffle to ensure random subsets are processed first

            for subset in subsets:
                # Calculate the number of codes to generate for this subset
                num_codes_subset = int((prob / 100) * max_total_codes / len(distribution))
                num_codes_subset = min(num_codes_subset, max_codes_per_subset)

                # Calculate the total possible combinations for the subset
                total_possible = len(subset) ** length
                if total_possible <= num_codes_subset:
                    # Generate all possible codes for the subset
                    for p in product(subset, repeat=length):
                        code = ''.join(p)
                        codes.append(code)
                        if len(codes) >= max_total_codes:
                            return codes
                else:
                    # Randomly sample codes to limit the number
                    sampled_codes = set()
                    while len(sampled_codes) < num_codes_subset:
                        code = ''.join(random.choices(subset, k=length))
                        sampled_codes.add(code)
                        if len(sampled_codes) >= total_possible:
                            break  # All possible codes have been sampled
                    codes.extend(sampled_codes)
                    if len(codes) >= max_total_codes:
                        return codes[:max_total_codes]

        # Handle the remaining 2% probability for using all available colors
        remaining_codes = int(0.02 * max_total_codes)
        for _ in range(remaining_codes):
            code = ''.join(random.choices(colors, k=length))
            codes.append(code)
            if len(codes) >= max_total_codes:
                break

        return codes[:max_total_codes]