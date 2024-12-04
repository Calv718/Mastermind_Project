import time
import random
from player import Player
from itertools import product, combinations, permutations
from collections import Counter

class LogicLegends(Player):

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
    
    def make_guess(self, board_length: int, colors: list[str], scsa_name: str, last_response: tuple[int, int, int]) -> str:
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
        # Calculate the remaining number of guesses allowed for this round
        remaining_guesses = self.max_guesses_per_round

        # If the maximum number of guesses for the round has been reached, use a fallback guess
        if remaining_guesses <= 0:
            return self.generate_fallback_guess(scsa_name, board_length, colors)

        # Dynamically generate the colors based on the color count
        generated_colors = self.generate_colors(len(colors))

        # Check the current search space size
        if self.possible_codes:
            search_space_size = len(self.possible_codes)
        else:
            # If no codes have been initialized, calculate potential search space size
            search_space_size = len(generated_colors) ** board_length

        # Switch to generating all products if the search space reaches 500,000
        if search_space_size <= 500_000 and not self.possible_codes:
            self.possible_codes = self.generate_combinations(colors, board_length)

        # Initialize possible codes using SCSA if not already initialized
        if not self.possible_codes:
            self.possible_codes = self.generate_possible_codes(scsa_name, board_length, generated_colors, remaining_guesses)

        start_time = time.time()  # Start the timer for time tracking

        # Filter codes based on the feedback from the last guess
        if self.previous_guesses and last_response != (0, 0, 0):
            last_guess = self.previous_guesses[-1]
            self.filter_possible_codes(last_guess, last_response)

        # Decide on the next guess based on the current search space
        guess = self.select_next_guess(scsa_name, board_length, generated_colors)

        # Ensure that the guess is legal before returning, otherwise attempt to make a legal fallback guess
        if not self.is_guess_legal(guess, board_length, generated_colors):
            guess = self.generate_fallback_guess(scsa_name, board_length, generated_colors)

        # Check if nearing time limit and adjust if necessary by reusing the last guess
        elapsed_time = time.time() - start_time
        if elapsed_time > self.time_cutoff - self.time_buffer and self.previous_guesses:
            guess = self.previous_guesses[-1]

        # Store the current guess and return it
        self.previous_guesses.append(guess)
        return guess

    def generate_possible_codes(self, scsa_name: str, length: int, colors: list[str], remaining_guesses: int) -> list[str]:
        """
        Generate all possible codes based on the selected SCSA.

        Args:
            scsa_name (str): The name of the SCSA.
            length (int): The length of the code to generate.
            colors (list[str]): The list of available colors.
            remaining_guesses (int): The number of guesses remaining for the round.

        Returns:
            list[str]: A list of possible codes.
        """
        # Dynamically retrieve the generator method based on SCSA name
        generator_method = getattr(self, f'generate_{scsa_name}', None)

        if generator_method:
            return generator_method(length, colors, remaining_guesses)
        else:
            raise ValueError(f"Unsupported SCSA: {scsa_name}")

    def filter_possible_codes(self, last_guess: str, feedback: tuple[int, int, int]):
        """
        Filter the possible codes based on the feedback from the last guess.

        Args:
            last_guess (str): The last guess made.
            feedback (tuple[int, int, int]): Feedback from the last guess.
        """
        # Retain only codes that are consistent with feedback
        self.possible_codes = [
            code for code in self.possible_codes
            if self.is_consistent_with_feedback(last_guess, code, feedback)
        ]

    def select_next_guess(self, scsa_name: str, length: int, colors: list[str]) -> str:
        """
        Select the next guess based on the current possible codes.

        Args:
            scsa_name (str): The name of SCSA.
            length (int): The length of the code to guess.
            colors (list[str]): The list of available colors.

        Returns:
            str: The selected next guess.
        """
        # If the search space is too large, use a heuristic to choose the guess
        if len(self.possible_codes) > 500_000:
            # print(f"Using heuristic_guess. Possible codes: {len(self.possible_codes)}")
            guess = self.heuristic_guess()
            # print(f"Heuristic guess selected: {guess}")
            return guess
        
        elif self.possible_codes:
            guess = self.possible_codes.pop(0) # Take the first possible code
            # print(f"Selected next guess from possible_codes: {guess}")
            return guess
        
        else:
            # print("No possible codes remaining. Generating fallback guess.")
            guess = self.generate_fallback_guess(scsa_name, length, colors)
            # print(f"Fallback guess: {guess}")
            return guess

    def is_consistent_with_feedback(self, guess: str, code: str, feedback: tuple[int, int, int]) -> bool:
        """
        Check if a given code is consistent with the feedback from the previous guess.

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
        # Calculate remaining guesses
        remaining_guesses = self.max_guesses_per_round

        # Attempt to generate a code using the specified SCSA
        generator_method = getattr(self, f'generate_{scsa_name}', None)
        if generator_method:
            possible_codes = generator_method(length, colors, remaining_guesses)
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
        Select the next guess using a heuristic to minimize the search space.

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

    def generate_colors(self, color_count: int) -> list[str]:
        """
        Generate a list of colors based on the color count.

        Args:
            color_count (int): The number of available colors (1-26).

        Returns:
            list[str]: A list of generated colors.
        """
        return [chr(65 + i) for i in range(color_count)]
    
    def sample_random_codes(self, colors: list[str], length: int, count: int) -> set[str]:
        """
        Generate a set of random codes with the specified length.

        Args:
            colors (list[str]): The list of allowed colors.
            length (int): The length of each code.
            count (int): The number of codes to generate.

        Returns:
            set[str]: A set of randomly generated codes.
        """
        codes = set()
        while len(codes) < count:
            codes.add(''.join(random.choices(colors, k=length)))

        return codes
    
    def generate_combinations(self, colors: list[str], length: int) -> list[str]:
        """
        Generate all possible combinations of codes for the given colors and length.

        Args:
            colors (list[str]): The list of allowed colors.
            length (int): The length of each code.

        Returns:
            list[str]: A list of all possible combinations.
        """
        return [''.join(p) for p in product(colors, repeat=length)]

    # ---------------------- SCSA-Specific Methods ----------------------

    def generate_InsertColors(self, length: int, colors: list[str], remaining_guesses: int) -> list[str]:
        """
        Generates a strategic subset of codes to balance diversity and efficiency.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of allowed colors.
            remaining_guesses (int): The remaining number of guesses allowed.

        Returns:
            list[str]: A list of generated codes.
        """
        colors = self.generate_colors(len(colors))
        max_codes = min(500, remaining_guesses)  # Limit codes to remaining guesses
        codes = set()

        # Step 1 -> Generate diverse codes with maximum unique colors
        while len(codes) < max_codes:
            # Randomly select unique colors up to the minimum of length or total colors available
            selected_colors = random.sample(colors, min(length, len(colors)))
            
            # If the selected colors don't fill the required length, pad with random choices
            while len(selected_colors) < length:
                selected_colors.append(random.choice(colors))
            
            # Shuffle the selected colors to create a randomized arrangement
            random.shuffle(selected_colors)
            
            # Add the generated code to the set
            codes.add(''.join(selected_colors))

        # Step 2 -> Use Cartesian product utility to fill remaining codes if needed
        if len(codes) < max_codes:
            # Generate all possible combinations of the given colors and length
            additional_combinations = self.generate_combinations(colors, length)
            
            # Add these combinations to the set until the desired number of codes is reached
            for combination in additional_combinations:
                if len(codes) >= max_codes:
                    break  # Stop adding once the maximum number of codes is reached
                codes.add(combination)

        # Convert the set of unique codes to a list and return
        return list(codes)

    def generate_TwoColor(self, length: int, colors: list[str], remaining_guesses: int) -> list[str]:
        """
        Generates codes containing exactly two distinct colors, ensuring both are used at least once.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of allowed colors.
            remaining_guesses (int): The remaining number of guesses allowed.

        Returns:
            list[str]: A list of generated codes.
        """
        # Ensure there are at least two colors available
        if len(colors) < 2:
            return []

        # List to store generated codes
        codes = []

        # Iterate over all combinations of two distinct colors
        for color1, color2 in combinations(colors, 2):
            usable_colors = [color1, color2]

            # Generate codes until remaining_guesses is satisfied
            while len(codes) < remaining_guesses:
                # Initialize code as a list with two guaranteed distinct colors
                code = [0] * length
                indices = random.sample(range(length), 2)
                code[indices[0]] = color1
                code[indices[1]] = color2

                # Fill the rest of the positions with the two colors randomly
                code = [
                    peg if peg != 0 else random.choice(usable_colors)
                    for peg in code
                ]

                # Convert code to string and add to the list
                codes.append(''.join(code))

                # Break early if remaining_guesses is satisfied
                if len(codes) >= remaining_guesses:
                    break

        # Return the generated codes
        return codes[:remaining_guesses]

    def generate_ABColor(self, length: int, colors: list[str], remaining_guesses: int) -> list[str]:
        """
        Generates codes containing only "A" and "B", ensuring both are present.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of allowed colors (ignored here since only 'A' and 'B' are used).
            remaining_guesses (int): The remaining number of guesses allowed.

        Returns:
            list[str]: A list of generated codes.
        """
        # Check if there are at least two colors available to use "A" and "B"
        if len(colors) < 2:
            return []  # Return an empty list if there are not enough colors

        # Generate all possible combinations of "A" and "B" for the given length
        combinations = [
            code for code in self.generate_combinations(['A', 'B'], length) if 'A' in code and 'B' in code
        ]

        # Limit the number of combinations to the remaining guesses
        return combinations[:remaining_guesses]

    def generate_TwoColorAlternating(self, length: int, colors: list[str], remaining_guesses: int) -> list[str]:
        """
        Generates codes that alternate between two distinct colors.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of allowed colors.
            remaining_guesses (int): The remaining number of guesses allowed.

        Returns:
            list[str]: A list of generated codes.
        """
        # Dynamically generate the list of colors based on the given color count
        colors = self.generate_colors(len(colors))

        # Initialize an empty list to store alternating patterns
        codes = []

        # Iterate through all combinations of two distinct colors
        for color1, color2 in combinations(colors, 2):
            # Generate an alternating pattern starting with the first color
            pattern1 = ''.join([color1 if i % 2 == 0 else color2 for i in range(length)])
            
            # Generate an alternating pattern starting with the second color
            pattern2 = ''.join([color2 if i % 2 == 0 else color1 for i in range(length)])
            
            # Add both patterns to the list of codes
            codes.extend([pattern1, pattern2])

            # Stop if the number of generated codes reaches the remaining guesses
            if len(codes) >= remaining_guesses:
                break

        # Return only the number of codes allowed by remaining_guesses
        return codes[:remaining_guesses]

    def generate_OnlyOnce(self, length: int, colors: list[str], remaining_guesses: int) -> list[str]:
        """
        Generates codes where each color appears at most once.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of allowed colors.
            remaining_guesses (int): The remaining number of guesses allowed.

        Returns:
            list[str]: A list of generated codes.
        """
        # Ensure the list of colors is dynamically generated
        colors = self.generate_colors(len(colors))

        # Handle edge case: No valid colors or length is zero
        if length == 0 or not colors:
            return []

        # Case 1: Code length <= number of colors
        if length <= len(colors):
            # Generate all unique combinations of the required length
            codes = self.generate_combinations(colors, length)
            return codes[:remaining_guesses]

        # Case 2: Code length > number of colors
        unique_part_length = len(colors)  # Max length with unique colors
        remaining_length = length - unique_part_length  # Extra positions to be filled

        # Generate unique part
        unique_part_codes = self.generate_combinations(colors, length)
        # List to store the final codes
        codes = []

        # Generate the extra part for remaining length
        for unique_code in unique_part_codes:
            # If remaining guesses have been met, exit early
            if len(codes) >= remaining_guesses:
                break

            # Randomly fill the remaining positions with any color
            extra_part = [''.join(random.choices(colors, k=remaining_length)) for _ in range(remaining_guesses - len(codes))]
            codes.extend(unique_code + extra for extra in extra_part)

        # Return only the allowed number of guesses
        return codes[:remaining_guesses]

    def generate_FirstLast(self, length: int, colors: list[str], remaining_guesses: int) -> list[str]:
        """
        Generates codes where the first and last colors are identical.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of allowed colors.
            remaining_guesses (int): The remaining number of guesses allowed.

        Returns:
            list[str]: A list of generated codes.
        """
        # Handle edge case for invalid code length
        if length < 2:
            return []  # Cannot generate valid "FirstLast" codes

        # Ensure we have at least one valid color
        if not colors:
            return []

        # Use a set to avoid duplicates and ensure unique codes
        codes = set()

        while len(codes) < remaining_guesses:
            # Randomly select the first/last color
            first_last_color = random.choice(colors)

            # Generate the middle part of the code
            if length == 2:
                # Special case: If length is 2, there is no middle part
                code = first_last_color * 2
            else:
                # Generate the middle part of the code randomly
                middle = ''.join(random.choices(colors, k=length - 2))
                code = first_last_color + middle + first_last_color

            # Add the code to the set
            codes.add(code)

        # Return the codes as a list, limited by remaining_guesses
        return list(codes)[:remaining_guesses]

    def generate_UsuallyFewer(self, length: int, colors: list[str], remaining_guesses: int) -> list[str]:
        """
        Generates codes that usually have fewer (2 or 3) colors, with a small probability of using all available colors.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of allowed colors.
            remaining_guesses (int): The remaining number of guesses allowed.

        Returns:
            list[str]: A list of generated codes.
        """
        # Dynamically generate the list of colors
        colors = self.generate_colors(len(colors))

        # Distribution of number of colors and their probabilities (percentage)
        distribution = [(2, 36), (3, 54), (len(colors), 10)]  # Fewer colors are more likely
        codes = set()  # Using a set to avoid duplicates

        for num_colors, prob in distribution:
            # Skip if the number of colors exceeds the available colors
            if num_colors > len(colors):
                continue

            # Generate all subsets of the specified number of colors
            subsets = list(combinations(colors, num_colors))
            random.shuffle(subsets)  # Shuffle subsets to ensure randomness

            # Calculate the maximum number of codes allowed per subset based on remaining guesses
            max_codes_per_subset = min(remaining_guesses - len(codes), int(prob / 100 * remaining_guesses))
            if max_codes_per_subset <= 0:
                break  # Exit early if no more guesses are allowed

            for subset in subsets:
                # Calculate the total possible combinations for the subset
                total_possible = len(subset) ** length
                if total_possible <= max_codes_per_subset:
                    # Generate all possible codes for the subset
                    for p in product(subset, repeat=length):
                        codes.add(''.join(p))

                        # Stop if the total codes exceed remaining guesses
                        if len(codes) >= remaining_guesses:
                            return list(codes)
                else:
                    # Randomly sample codes to limit the number for larger subsets
                    sampled = set()
                    while len(sampled) < max_codes_per_subset and len(codes) < remaining_guesses:
                        code = ''.join(random.choices(subset, k=length))
                        sampled.add(code)
                    codes.update(sampled)

                    # Stop if the total codes exceed remaining guesses
                    if len(codes) >= remaining_guesses:
                        return list(codes)

            # Stop if the total codes exceed remaining guesses
            if len(codes) >= remaining_guesses:
                break

        return list(codes)[:remaining_guesses]

    def generate_PreferFewer(self, length: int, colors: list[str], remaining_guesses: int) -> list[str]:
        """
        SCSA: PreferFewer - Generates codes with a preference for fewer colors based on a specific probability distribution,
        adhering to the constraints of time and a maximum of 100 guesses.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of available colors.
            remaining_guesses (int): The remaining guesses allowed in the round.

        Returns:
            list[str]: A list of generated codes.
        """
        codes = []
        max_total_codes = min(remaining_guesses, 500_000)  # Adjust to avoid exceeding the guess limit
        max_codes_per_subset = 100  # Adjust to ensure subsets are processed efficiently
        start_time = time.time()
        max_time = 5  # Maximum time allowed in seconds

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
                # Check elapsed time
                if time.time() - start_time > max_time - 0.1:
                    return codes  # Return codes generated so far

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
                        if len(codes) >= max_total_codes or len(codes) >= remaining_guesses:
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
                    if len(codes) >= max_total_codes or len(codes) >= remaining_guesses:
                        return codes[:max_total_codes]

        # Handle the remaining 2% probability for using all available colors
        remaining_codes = min(int(0.02 * max_total_codes), remaining_guesses - len(codes))
        for _ in range(remaining_codes):
            if time.time() - start_time > max_time - 0.1:
                break
            code = ''.join(random.choices(colors, k=length))
            codes.append(code)
            if len(codes) >= max_total_codes or len(codes) >= remaining_guesses:
                break

        return codes[:max_total_codes]

    # --------------------------- Utility Methods --------------------------

    def generate_symmetric_code(self, length: int, allowed_colors: list[str], remaining_guesses: int) -> str:
        """
        Generate a symmetric code based on the given length and allowed colors.

        Args:
            length (int): The length of the code to generate.
            allowed_colors (list[str]): The list of allowed colors.
            remaining_guesses (int): Remaining guesses allowed in the current round.

        Returns:
            str: A symmetric code of the given length.
        """
        half_length = length // 2
        first_half = ''.join(random.choices(allowed_colors, k=half_length))

        if length % 2 == 0:
            return first_half + first_half[::-1]  # Symmetry for even lengths
        else:
            middle_color = random.choice(allowed_colors)
            return first_half + middle_color + first_half[::-1]  # Symmetry for odd lengths

    def generate_segmented_code(self, length: int, allowed_colors: list[str], segment_length: int, remaining_guesses: int) -> str:
        """
        Generate a code with repeating segments based on the segment length.

        Args:
            length (int): The length of the code to generate.
            allowed_colors (list[str]): The list of allowed colors.
            segment_length (int): The length of each repeating segment.
            remaining_guesses (int): Remaining guesses allowed in the current round.

        Returns:
            str: A segmented code of the given length.
        """
        segment = ''.join(random.choices(allowed_colors, k=segment_length))
        return (segment * (length // segment_length)) + segment[:length % segment_length]

    # ---------------------- Mystery-Specific Methods ----------------------

    def helper_Mystery1(self, length: int, allowed_colors: list[str], 
                    starting_patterns: list[str], dominant_patterns: list[str],
                    unique_color_weights: list[float], probabilities: dict) -> str:
        """
        Helper function to generate a single Mystery1 code.

        Args:
            length (int): The length of the code to generate.
            allowed_colors (list[str]): The list of allowed colors.
            starting_patterns (list[str]): List of frequent starting patterns.
            dominant_patterns (list[str]): List of dominant patterns.
            unique_color_weights (list[float]): Weights for unique color selection.
            probabilities (dict): Probabilities for special pattern logic.

        Returns:
            str: A single generated code.
        """
        # Decide if a special pattern will be used
        use_special_pattern = random.random() < probabilities["special_pattern"]

        if use_special_pattern:
            # Use predefined/symmetrical patterns
            if random.random() < 0.3:
                start = random.choice(starting_patterns)
                remaining_length = max(0, length - len(start))
                selected_colors = random.sample(allowed_colors, k=remaining_length)
                code = start + ''.join(random.choices(selected_colors, k=remaining_length))

            # Dominant patterns
            elif random.random() < 0.3:
                start = random.choice(dominant_patterns)
                remaining_length = max(0, length - len(start))
                code = start + ''.join(random.choices(allowed_colors, k=remaining_length))
            
            # Generate dynamic symmetry
            else:
                half_length = length // 2
                first_half = ''.join(random.choices(allowed_colors, k=half_length))

                # Even-length symmetry
                if length % 2 == 0:
                    code = first_half + first_half[::-1]
                
                # Odd-length symmetry
                else:
                    middle_color = random.choice(allowed_colors)
                    code = first_half + middle_color + first_half[::-1]

        else:
            # Determine if full repetition is used
            if random.random() < probabilities["full_repetition"]:
                full_repetition_color = random.choice(allowed_colors)
                code = full_repetition_color * length

            else:
                # Standard generation logic
                num_unique_colors = random.choices(
                    [1, 2, max(5, len(allowed_colors) // 2)], weights=unique_color_weights
                )[0]
                selected_colors = random.sample(allowed_colors, min(num_unique_colors, len(allowed_colors)))
                code = ''.join(random.choices(selected_colors, k=length))

        return code

    def generate_Mystery1(self, length: int, colors: list[str], remaining_guesses: int) -> list[str]:
        """
        Generate codes for Mystery1 SCSA with dataset-specific constraints:
        - For smaller spaces (<= 500,000), generate all product combinations.
        - For larger spaces, use observed patterns and dynamically generated symmetrical patterns.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of allowed colors.
            remaining_guesses (int): Remaining guesses allowed in the current round.

        Returns:
            list[str]: A list of generated codes.
        """
        # Dynamically generate the list of allowed colors
        allowed_colors = self.generate_colors(len(colors))

        # Dynamically create starting and dominant patterns based on available colors
        starting_patterns = [c * 2 for c in allowed_colors[:5]]  # Top 5 frequent starting patterns
        dominant_patterns = [c * 4 for c in allowed_colors[:3]]  # Top 3 dominant patterns

        max_total_codes = 500_000  # Maximum total codes to prevent excessive memory usage
        total_combinations = len(allowed_colors) ** length

        # Probabilities and weights for pattern generation
        unique_color_weights = [0.25, 0.35, 0.4]
        probabilities = {
            "special_pattern": 0.6,  # Probability of using a special pattern
            "use_symmetry": 0.3,     # Probability of generating a symmetrical pattern
            "full_repetition": 0.2   # Probability of full repetition
        }

        if total_combinations <= max_total_codes:
            # Generate all Cartesian products
            return [''.join(p) for p in product(allowed_colors, repeat=length)]

        else:
            # Generate constrained codes based on observed patterns
            codes = set()
            max_codes = min(1000, remaining_guesses)

            # Assign code generation to the helper function
            while len(codes) < max_codes:
                code = self.helper_Mystery1(
                    length, allowed_colors, starting_patterns, dominant_patterns,
                    unique_color_weights, probabilities
                )
                codes.add(code)

            return list(codes)
    
    def helper_Mystery2(self, length: int, allowed_colors: list[str], 
                    probabilities: dict, cycle_lengths: list[int]) -> str:
        """
        Helper function to generate a single Mystery2 code.

        Args:
            length (int): The length of the code to generate.
            allowed_colors (list[str]): The list of allowed colors.
            probabilities (dict): Probabilities for special pattern logic.
            cycle_lengths (list[int]): List of possible cycle lengths for cyclic patterns.

        Returns:
            str: A single generated code.
        """
        # Decide if a cyclic pattern will be used
        use_cyclic_pattern = random.random() < probabilities.get("cyclic_pattern", 0.7)

        # Generate a cyclic pattern
        if use_cyclic_pattern and cycle_lengths:
            cycle_length = random.choice(cycle_lengths)
            cycle = ''.join(random.choices(allowed_colors, k=cycle_length))
            code = (cycle * (length // cycle_length)) + cycle[:length % cycle_length]

        # Increased randomness probability
        elif random.random() < probabilities.get("random_pattern", 0.3):
            code = ''.join(random.choices(allowed_colors, k=length))

        else:
            # Fallback to a random sequence (if no specific pattern is selected)
            code = ''.join(random.choices(allowed_colors, k=length))

        return code

    def generate_Mystery2(self, length: int,colors: list[str], remaining_guesses: int) -> list[str]:
        """
        Generate codes for Mystery2 SCSA with dataset-specific constraints:
        - For smaller spaces (<= 500,000) -> generate all product combinations.
        - For larger spaces -> use cyclic patterns and dynamically generated patterns.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of allowed colors.
            remaining_guesses (int): Remaining guesses allowed in the current round.

        Returns:
            list[str]: A list of generated codes.
        """
        # Dynamically generate the list of allowed colors
        allowed_colors = self.generate_colors(len(colors))

        max_total_codes = 500_000  # Maximum total codes to prevent excessive memory usage
        total_combinations = len(allowed_colors) ** length

        # Constraints for Mystery2
        cycle_lengths = [3, 4, 5]  # Possible lengths for cyclic patterns
        probabilities = {
            "cyclic_pattern": 0.7,  # Probability of using a cyclic pattern
            "random_pattern": 0.3   # Probability of a completely random pattern
        }

        if total_combinations <= max_total_codes:
            # Generate all Cartesian products
            return [''.join(p) for p in product(allowed_colors, repeat=length)]
        
        else:
            # Generate constrained codes based on cyclic patterns
            codes = set()
            max_codes = min(1000, remaining_guesses)

            while len(codes) < max_codes:
                code = self.helper_Mystery2(
                    length=length,
                    allowed_colors=allowed_colors,
                    probabilities=probabilities,
                    cycle_lengths=cycle_lengths
                )
                codes.add(code)

            return list(codes)
    
    def helper_Mystery3(self, length: int, allowed_colors: list[str], probabilities: dict) -> str:
        """
        Helper function to generate a single Mystery3 code.

        Args:
            length (int): The length of the code to generate.
            allowed_colors (list[str]): The list of allowed colors.
            probabilities (dict): Probabilities for special pattern logic.

        Returns:
            str: A single generated code.
        """
        # Decide if segments should repeat
        use_repeating_segments = random.random() < probabilities.get("repeating_segments", 0.7)

        if use_repeating_segments:
            # Generate repeating or interleaved segments
            segment_length = random.randint(2, 4)  # Length of each segment
            segment = ''.join(random.choices(allowed_colors, k=segment_length))
            code = (segment * (length // segment_length)) + segment[:length % segment_length]

        else:
            # Generate a completely random code
            code = ''.join(random.choices(allowed_colors, k=length))

        return code

    def generate_Mystery3(self, length: int, colors: list[str], remaining_guesses: int) -> list[str]:
        """
        Generate codes for Mystery3 SCSA with dataset-specific constraints:
        - For smaller spaces (<= 500,000) -> generate all product combinations.
        - For larger spaces -> use alternating and repeating segments.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of allowed colors.
            remaining_guesses (int): Remaining guesses allowed in the current round.

        Returns:
            list[str]: A list of generated codes.
        """
        # Dynamically generate the list of allowed colors
        allowed_colors = self.generate_colors(len(colors))

        max_total_codes = 500_000  # Maximum total codes to prevent excessive memory usage
        total_combinations = len(allowed_colors) ** length

        # Probabilities for Mystery3 patterns
        probabilities = {
            "repeating_segments": 0.7,  # Probability of repeating/interleaved segments
            "random_pattern": 0.3       # Probability of generating a completely random pattern
        }

        if total_combinations <= max_total_codes:
            # Generate all Cartesian products
            return [''.join(p) for p in product(allowed_colors, repeat=length)]
        
        else:
            # Generate constrained codes based on alternating/repeating segments
            codes = set()
            max_codes = min(1000, remaining_guesses)

            while len(codes) < max_codes:
                code = self.helper_Mystery3(length, allowed_colors, probabilities)
                codes.add(code)

            return list(codes)
    
    def helper_Mystery4(self, length: int, allowed_colors: list[str], probabilities: dict) -> str:
        """
        Helper function to generate a single Mystery4 code.

        Args:
            length (int): The length of the code to generate.
            allowed_colors (list[str]): The list of allowed colors.
            probabilities (dict): Probabilities for special pattern logic.

        Returns:
            str: A single generated code.
        """
        # Decide if full repetition is used
        if random.random() < probabilities.get("full_repetition", 0.4):
            full_repetition_color = random.choice(allowed_colors)
            return full_repetition_color * length

        # Decide if segmented repetition is used
        elif random.random() < probabilities.get("segmented_repetition", 0.3):
            segment_length = random.randint(2, 4)
            return self.generate_segmented_code(length, allowed_colors, segment_length)

        # Decide if symmetry is used
        elif random.random() < probabilities.get("symmetry", 0.2):
            return self.generate_symmetric_code(length, allowed_colors)

        # Default to alternating/random structure
        else:
            return ''.join(random.choices(allowed_colors, k=length))

    def generate_Mystery4(self, length: int, colors: list[str], remaining_guesses: int) -> list[str]:
        """
        Generate codes for Mystery4 SCSA with dataset-specific constraints:
        - For smaller spaces (<= 500,000) -> generate all product combinations.
        - For larger spaces -> use observed patterns and dynamically generated symmetrical patterns.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of allowed colors.
            remaining_guesses (int): Remaining guesses allowed in the current round.

        Returns:
            list[str]: A list of generated codes.
        """
        # Dynamically generate the list of allowed colors
        allowed_colors = self.generate_colors(len(colors))

        max_total_codes = 500_000  # Maximum total codes to prevent excessive memory usage
        total_combinations = len(allowed_colors) ** length

        # Probabilities for Mystery4 patterns
        probabilities = {
            "full_repetition": 0.4,         # Probability of full repetition
            "segmented_repetition": 0.3,    # Probability of segmented repetition
            "symmetry": 0.2,                # Probability of symmetry
            "random_alternation": 0.1       # Probability of alternating/random structure
        }

        if total_combinations <= max_total_codes:
            # Generate all Cartesian products
            return [''.join(p) for p in product(allowed_colors, repeat=length)]
        
        else:
            # Generate constrained codes based on observed patterns
            codes = set()
            max_codes = min(1000, remaining_guesses)

            while len(codes) < max_codes:
                code = self.helper_Mystery4(length, allowed_colors, probabilities)
                codes.add(code)

            return list(codes)

    def helper_Mystery5(self, length: int, allowed_colors: list[str], probabilities: dict) -> str:
        """
        Helper function to generate a single Mystery5 code.

        Args:
            length (int): The length of the code to generate.
            allowed_colors (list[str]): The list of allowed colors.
            probabilities (dict): Probabilities for special pattern logic.

        Returns:
            str: A single generated code.
        """
        # Decide if an alternating pattern will be used
        if random.random() < probabilities.get("alternating_pattern", 0.5):
            colors = random.sample(allowed_colors, k=2)
            return ''.join(colors[i % 2] for i in range(length))

        # Decide if symmetry will be used
        elif random.random() < probabilities.get("symmetry", 0.3):
            return self.generate_symmetric_code(length, allowed_colors)

        # Use repeated subsegments
        else:
            segment_length = random.randint(3, 5)
            return self.generate_segmented_code(length, allowed_colors, segment_length)
        
    def generate_Mystery5(self, length: int, color: list[str], remaining_guesses: int) -> list[str]:
        """
        Generate codes for Mystery5 SCSA with dataset-specific constraints:
        - For smaller spaces (<= 500,000) -> generate all product combinations.
        - For larger spaces -> use observed patterns and dynamically generated alternating patterns.

        Args:
            length (int): The length of the code to generate.
            colors (list[str]): The list of allowed colors.
            remaining_guesses (int): Remaining guesses allowed in the current round.

        Returns:
            list[str]: A list of generated codes.
        """
        # Dynamically generate the list of allowed colors based on color_count
        allowed_colors = self.generate_colors(len(color))

        max_total_codes = 500_000  # Maximum total codes to prevent excessive memory usage
        total_combinations = len(allowed_colors) ** length

        # Probabilities for Mystery5 patterns
        probabilities = {
            "alternating_pattern": 0.5,  # Probability of alternating patterns
            "symmetry": 0.3,            # Probability of symmetry
            "repeated_subsegments": 0.2 # Probability of repeated subsegments
        }

        if total_combinations <= max_total_codes:
            # Generate all Cartesian products
            return [''.join(p) for p in product(allowed_colors, repeat=length)]
        
        else:
            # Generate constrained codes based on observed patterns
            codes = set()
            max_codes = min(1000, remaining_guesses)

            while len(codes) < max_codes:
                code = self.helper_Mystery5(length, allowed_colors, probabilities)
                codes.add(code)

            return list(codes)

    def generate_Mystery6(self, length: int, colors: list[str]) -> list[str]:
        """
        A placeholder generator used to generate the possible codes for mystery6 SCSA
        """
        # Uses a list comprehension for efficient generation of all possible combinations
        return [''.join(p) for p in product(colors, repeat=length)]

    def generate_Mystery7(self, length: int, colors: list[str]) -> list[str]:
        """
        A placeholder generator used to generate the possible codes for mystery7 SCSA
        """
        # Uses a list comprehension for efficient generation of all possible combinations
        return [''.join(p) for p in product(colors, repeat=length)]