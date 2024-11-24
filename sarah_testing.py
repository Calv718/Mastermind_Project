import time
import random
from player import *
from itertools import product
from functools import lru_cache
from collections import deque

class LogicLegends(Player):
    def __init__(self):
        super().__init__()
        self.player_name = "LogicLegends"
        self.possible_codes = deque()  
        self.previous_guesses = []
        self.previous_feedback = []
        self.time_cutoff = 5
        self.time_buffer = 0.1

    def insert_colors(self, board_length: int, colors: list[str]) -> list[str]:
        codes = [''.join(p) for p in product(colors, repeat=board_length)]
        return codes

    def two_color(self, board_length: int, colors: list[str]) -> list[str]:
        if len(colors) < 2:
            return []
        usable_colors = random.sample(colors, k=2)
        return [''.join(random.choices(usable_colors, k=board_length)) for _ in range(1000)]

    def ab_color(self, board_length: int) -> list[str]:
        usable_colors = ["A", "B"]
        return [''.join(random.choices(usable_colors, k=board_length)) for _ in range(1000)]

    def two_color_alternating(self, board_length: int, colors: list[str]) -> list[str]:
        if len(colors) < 2:
            return []
        first_color, second_color = random.sample(colors, k=2)
        return [
            ''.join(first_color if i % 2 == 0 else second_color for i in range(board_length)) for _ in range(1000)
        ]

    def only_once(self, board_length: int, colors: list[str]) -> list[str]:
        if len(colors) < board_length:
            return []
        return [''.join(random.sample(colors, k=board_length)) for _ in range(1000)]

    def first_last(self, board_length: int, colors: list[str]) -> list[str]:
        if len(colors) < 1:
            return []
        return [
            ''.join([color] + random.choices(colors, k=board_length - 2) + [color])
            for color in random.choices(colors, k=1000)
        ]

    def usually_fewer(self, board_length: int, colors: list[str]) -> list[str]:
        if len(colors) < 3:
            return []
        codes = []
        for _ in range(1000):
            if random.randint(0, 100) < 90:  # 90% chance
                picked_colors = random.sample(colors, k=random.randint(2, 3))
            else:
                picked_colors = colors
            codes.append(''.join(random.choices(picked_colors, k=board_length)))
        return codes

    def prefer_fewer(self, board_length: int, colors: list[str]) -> list[str]:
        if len(colors) < 2:
            return []
        codes = []
        for _ in range(1000):
            probability = random.randint(0, 100)
            if probability <= 49:
                picked_colors = random.sample(colors, k=1)
            elif probability <= 74:
                picked_colors = random.sample(colors, k=2)
            elif probability <= 87:
                picked_colors = random.sample(colors, k=min(3, len(colors)))
            elif probability <= 95:
                picked_colors = random.sample(colors, k=min(4, len(colors)))
            elif probability <= 98:
                picked_colors = random.sample(colors, k=min(5, len(colors)))
            else:
                picked_colors = colors
            codes.append(''.join(random.choices(picked_colors, k=board_length)))
        return codes

    def default_codes(self, board_length: int, colors: list[str]) -> list[str]:
        return [''.join(p) for p in product(colors, repeat=board_length)]

    def generate_possible_codes(self, board_length: int, colors: list[str], scsa_name: str) -> list[str]:
        """Generates possible codes with optimized SCSA constraints applied."""
        if scsa_name == "InsertColors":
            return self.insert_colors(board_length, colors)
        elif scsa_name == "TwoColor":
            return self.two_color(board_length, colors)
        elif scsa_name == "ABColor":
            return self.ab_color(board_length)
        elif scsa_name == "TwoColorAlternating":
            return self.two_color_alternating(board_length, colors)
        elif scsa_name == "OnlyOnce":
            return self.only_once(board_length, colors)
        elif scsa_name == "FirstLast":
            return self.first_last(board_length, colors)
        elif scsa_name == "UsuallyFewer":
            return self.usually_fewer(board_length, colors)
        elif scsa_name == "PreferFewer":
            return self.prefer_fewer(board_length, colors)
        else:
            return self.default_codes(board_length, colors)

    def make_guess(self, board_length: int, colors: list[str], scsa_name: str, last_response: tuple[int, int, int]) -> str:
        start_time = time.time()
        if not self.possible_codes:
            self.possible_codes = self.generate_possible_codes(board_length, colors, scsa_name)

        if self.previous_guesses:
            last_guess = self.previous_guesses[-1]
            self.filter_possible_codes(last_guess, last_response)

        if time.time() - start_time > self.time_cutoff - self.time_buffer:
            guess = ''.join(random.choices(colors, k=board_length))
        else:
            guess = self.select_informative_guess(board_length, colors)

        self.previous_guesses.append(guess)
        self.previous_feedback.append(last_response)
        return guess

    def filter_possible_codes(self, last_guess: str, last_response: tuple[int, int, int]):
        filtered_codes = []
        for code in self.possible_codes:
            if self.is_consistent_with_feedback_cached(last_guess, code, last_response):
                filtered_codes.append(code)
        self.possible_codes = filtered_codes

    def select_informative_guess(self, board_length: int, colors: list[str]) -> str:
        if not self.possible_codes:
            return ''.join(random.choices(colors, k=board_length))

        if len(self.possible_codes) < 10:
            return self.possible_codes[0]

        # Prioritize guesses that maximize color diversity
        color_distribution = {color: 0 for color in colors}
        for code in self.possible_codes:
            for color in set(code):
                color_distribution[color] += 1

        # Select the guess that uses the most frequently occurring colors
        sorted_colors = sorted(colors, key=lambda c: color_distribution[c], reverse=True)
        guess = ''.join(random.choices(sorted_colors, k=board_length))
        return guess


    @lru_cache(maxsize=None)
    def is_consistent_with_feedback_cached(self, guess: str, code: str, feedback: tuple[int, int, int]) -> bool:
        exact_matches = sum(1 for g, c in zip(guess, code) if g == c)
        guess_counts = {color: guess.count(color) for color in set(guess)}
        code_counts = {color: code.count(color) for color in set(code)}
        almost_matches = sum(min(guess_counts.get(color, 0), code_counts.get(color, 0)) for color in set(guess)) - exact_matches
        return (exact_matches, almost_matches, feedback[2]) == feedback
