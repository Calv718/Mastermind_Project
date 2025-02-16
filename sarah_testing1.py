import random
from player import Player
from collections import defaultdict
from itertools import product
from collections import Counter

class LogicLegends(Player):
    def __init__(self):
        """
        Initializes the LogicLegends player.
        """
        super().__init__()
        self.player_name = "LogicLegends"
        self.colors = []  # List of possible colors
        self.board_length = 0  # Number of pegs in the code
        self.scsa_name = ""  # Name of the Simplified Code Selection Algorithm (SCSA)
        self.previous_guesses = []  # List of previous guesses made
        self.previous_feedback = []  # List of feedback received for each guess
        self.possible_codes = []  # List of possible codes based on constraints
        self.possible_colors_per_position = []  # Possible colors for each position
        self.global_color_counts = {}  # Minimum and maximum counts for each color in the code

    def make_guess(
        self,
        board_length: int,
        colors: list[str],
        scsa_name: str,
        last_response: tuple[int, int, int],
    ) -> str:
        """
        Main method to make a guess in the game.

        Args:
            board_length (int): Number of pegs in the code.
            colors (list[str]): List of possible colors.
            scsa_name (str): Name of the SCSA.
            last_response (tuple[int, int, int]): Feedback from the last guess.

        Returns:
            str: The next guess.
        """
        self.board_length = board_length
        self.colors = colors
        self.scsa_name = scsa_name

        # Initialize variables on the first guess
        if not self.previous_guesses:
            self.initialize()

        # Update constraints based on the last feedback
        if self.previous_feedback:
            last_guess = self.previous_guesses[-1]
            last_feedback = self.get_feedback_tuple(last_response)
            self.update_constraints(last_guess, last_feedback)

        # Select the strategy based on the SCSA
        if scsa_name == "InsertColors":
            guess = self.strategy_insert_colors()
        elif scsa_name == "OnlyOnce":
            guess = self.strategy_only_once()
        elif scsa_name == "FirstLast":
            guess = self.strategy_first_last()
        elif scsa_name in ["TwoColor", "ABColor", "TwoColorAlternating"]:
            guess = self.strategy_two_color()
        elif scsa_name in ["UsuallyFewer", "PreferFewer"]:
            guess = self.strategy_prefer_fewer()
        else:
            # Default strategy if no specific SCSA is matched
            guess = self.strategy_default()

        # Store the guess
        self.previous_guesses.append(guess)
        return guess


    def initialize(self):
        """
        Initializes data structures and variables common to all strategies.
        """
        # Initialize possible colors per position with all colors
        self.possible_colors_per_position = [set(self.colors) for _ in range(self.board_length)]

        # Initialize global color counts (min and max occurrences of each color)
        self.global_color_counts = {color: [0, self.board_length] for color in self.colors}

        # Initialize possible codes for strategies that require it
        total_possible_codes = len(self.colors) ** self.board_length
        if total_possible_codes <= 500000:
            self.possible_codes = [''.join(p) for p in product(self.colors, repeat=self.board_length)]
            self.initialize_feedback_lookup()  # Precompute feedback
        else:
            self.possible_codes = None


    def initialize_feedback_lookup(self):
        """
        Precomputes feedback for all possible (guess, code) pairs.
        """
        self.feedback_lookup = {}
        if self.possible_codes:
            for guess in self.possible_codes:
                for code in self.possible_codes:
                    feedback = self.compute_feedback(guess, code)
                    self.feedback_lookup[(guess, code)] = feedback



    def get_feedback_tuple(self, response: tuple[int, int, int]) -> tuple[int, int]:
        """
        Extracts the exact and partial matches from the last response.

        Args:
            response (tuple[int, int, int]): Feedback from the last guess.

        Returns:
            tuple[int, int]: A tuple containing exact and partial matches.
        """
        exact_matches = response[0]
        partial_matches = response[1]

        # Store the feedback for future reference
        self.previous_feedback.append((exact_matches, partial_matches))
        return (exact_matches, partial_matches)


    def update_constraints(self, last_guess: str, last_feedback: tuple[int, int]):
        """
        Updates possible colors and global color counts based on feedback.

        Args:
            last_guess (str): The last guess made.
            last_feedback (tuple[int, int]): Feedback from the last guess.
        """
        exact_matches, partial_matches = last_feedback
        total_matches = exact_matches + partial_matches

        # Count occurrences of each color in the last guess
        guess_color_counts = defaultdict(int)
        for color in last_guess:
            guess_color_counts[color] += 1

        # If there are no matches, remove guessed colors from all positions
        if total_matches == 0:
            for color in set(last_guess):
                for pos_colors in self.possible_colors_per_position:
                    pos_colors.discard(color)
        else:
            # Cannot make strong positional eliminations without specific feedback
            # Placeholder for advanced constraint updates
            pass

        # Update global color counts for each color
        for color in self.colors:
            min_count, max_count = self.global_color_counts[color]
            color_in_guess = guess_color_counts.get(color, 0)
            if color_in_guess > 0:
                # Adjust min and max counts based on feedback
                max_possible = min(max_count, color_in_guess)
                min_possible = max(min_count, total_matches - (self.board_length - color_in_guess))
                self.global_color_counts[color] = [min_possible, max_possible]


    def strategy_insert_colors(self) -> str:
        """
        Strategy for the InsertColors SCSA where colors are selected at random.

        Returns:
            str: The next guess.
        """
        if self.possible_codes is not None:
            if self.previous_feedback:
                # Filter possible codes based on feedback
                last_guess = self.previous_guesses[-1]
                last_feedback = self.previous_feedback[-1]
                self.update_possible_codes(last_guess, last_feedback)
            if self.possible_codes:
                # Select next guess from possible codes
                guess = random.choice(self.possible_codes)
            else:
                # If no possible codes remain, make a random guess
                guess = ''.join(random.choices(self.colors, k=self.board_length))
        else:
            # For large board sizes, use a heuristic approach
            guess = self.generate_guess()
        return guess


    def strategy_only_once(self) -> str:
        """
        Strategy for the OnlyOnce SCSA where each color appears only once.

        Returns:
            str: The next guess.
        """
        # Ensure no repeated colors in the guess
        available_colors = set(self.colors)
        guess = ''
        for idx in range(self.board_length):
            possible_colors = self.possible_colors_per_position[idx] & available_colors
            if possible_colors:
                # Choose a color not used yet
                color = random.choice(list(possible_colors))
                guess += color
                available_colors.discard(color)
            else:
                # If no unique colors left, choose any possible color
                guess += random.choice(list(self.possible_colors_per_position[idx]))
        return guess


    def strategy_first_last(self) -> str:
        """
        Strategy for the FirstLast SCSA where the first and last pegs are the same color.

        Returns:
            str: The next guess.
        """
        # Find colors that could be in both first and last positions
        possible_first_last_colors = self.possible_colors_per_position[0] & self.possible_colors_per_position[-1]
        if possible_first_last_colors:
            color = random.choice(list(possible_first_last_colors))
        else:
            color = random.choice(self.colors)
        # Construct the guess
        guess = color  # First peg
        for idx in range(1, self.board_length - 1):
            possible_colors = self.possible_colors_per_position[idx]
            if possible_colors:
                guess += random.choice(list(possible_colors))
            else:
                guess += random.choice(self.colors)
        if self.board_length > 1:
            guess += color  # Last peg
        return guess


    def strategy_two_color(self) -> str:
        """
        Strategy for SCSAs that use only two colors.

        Returns:
            str: The next guess.
        """
        if not hasattr(self, 'two_colors'):
            if self.scsa_name == "ABColor":
                # Use specific colors 'A' and 'B'
                self.two_colors = ['A', 'B']
            else:
                # Randomly select two colors
                self.two_colors = random.sample(self.colors, k=2)
            # Limit possible colors per position to these two colors
            self.possible_colors_per_position = [set(self.two_colors) for _ in range(self.board_length)]
        # Generate the guess using the two colors
        guess = ''.join(random.choices(self.two_colors, k=self.board_length))
        return guess


    def strategy_prefer_fewer(self) -> str:
        """
        Strategy for SCSAs that prefer using fewer colors.

        Returns:
            str: The next guess.
        """
        if not hasattr(self, 'preferred_colors'):
            # Randomly decide to use 1 to 3 colors
            num_colors = random.choice([1, 2, 3])
            # Select preferred colors
            self.preferred_colors = random.sample(self.colors, k=min(num_colors, len(self.colors)))
            # Update possible colors per position
            self.possible_colors_per_position = [set(self.preferred_colors) for _ in range(self.board_length)]
        # Generate the guess using preferred colors
        guess = ''.join(random.choices(self.preferred_colors, k=self.board_length))
        return guess


    def strategy_default(self) -> str:
        """
        Default strategy when no specific SCSA applies.

        Returns:
            str: The next guess.
        """
        # Generate a guess based on constraints
        guess = self.generate_guess()
        return guess


    def generate_guess(self) -> str:
        """
        Generates a guess based on possible colors per position and global color probabilities.

        Returns:
            str: The generated guess.
        """
        # Calculate estimated probabilities for each color
        color_probabilities = {}
        total_max_counts = sum(self.global_color_counts[color][1] for color in self.colors)
        for color in self.colors:
            min_count, max_count = self.global_color_counts[color]
            if total_max_counts > 0:
                # Estimate probability based on min and max counts
                color_probabilities[color] = (min_count + max_count) / (2 * total_max_counts)
            else:
                color_probabilities[color] = 0  # Default to zero if no information

        # Build the guess
        guess = ''
        for idx in range(self.board_length):
            possible_colors = self.possible_colors_per_position[idx]
            if possible_colors:
                # Assign weights to possible colors based on estimated probabilities
                colors_weights = [(color, color_probabilities[color]) for color in possible_colors]
                total_weight = sum(weight for _, weight in colors_weights)
                if total_weight > 0:
                    # Normalize weights and choose a color
                    weights = [weight / total_weight for _, weight in colors_weights]
                    guess += random.choices([color for color, _ in colors_weights], weights=weights)[0]
                else:
                    # If weights sum to zero, choose randomly
                    guess += random.choice(list(possible_colors))
            else:
                # If no possible colors, choose any color (should not happen)
                guess += random.choice(self.colors)
        return guess


    def update_possible_codes(self, last_guess: str, last_feedback: tuple[int, int]):
        """
        Updates the list of possible codes based on the last feedback.
        """
        self.possible_codes = [
            code for code in self.possible_codes
            if self.compute_feedback(last_guess, code) == last_feedback
        ]


    def compute_feedback(self, guess: str, code: str) -> tuple[int, int]:
        """
        Computes the feedback for a guess against a code.
        """
        exact_matches = sum(g == c for g, c in zip(guess, code))
        guess_counts = Counter(guess)
        code_counts = Counter(code)
        total_color_matches = sum((guess_counts & code_counts).values())
        partial_matches = total_color_matches - exact_matches
        return (exact_matches, partial_matches)




    def is_consistent_with_feedback(self, guess: str, code: str, feedback: tuple[int, int]) -> bool:
        """
        Checks if a code is consistent with the feedback received for a guess.

        Args:
            guess (str): The guess made.
            code (str): The code to check.
            feedback (tuple[int, int]): Feedback from the guess.

        Returns:
            bool: True if consistent, False otherwise.
        """
        exact_matches = sum(g == c for g, c in zip(guess, code))
        guess_counts = Counter(guess)
        code_counts = Counter(code)
        total_color_matches = sum((guess_counts & code_counts).values())
        partial_matches = total_color_matches - exact_matches
        return (exact_matches, partial_matches) == feedback