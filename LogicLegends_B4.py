"""
Below is the implementation of a Player class using the baseline strategy B4 from the Project Description:

B4: The article by Rao (posted on Blackboard) has a heuristic algorithm that is probably not optimal.

"""

import time
import random
from player import *
# from itertools import product

# class Baseline4(Player):
#     def __init__(self):
#         super().__init__()
#         self.player_name = "Baseline4"
#         self.possible_codes = []


from abc import ABC, abstractmethod
from typing import List, Tuple, Set, Dict
from collections import defaultdict


from abc import ABC, abstractmethod
from typing import List, Tuple, Set, Dict
from collections import defaultdict

class Baseline4(Player):
    """Baseline4 implementation of Mastermind Player"""

    def __init__(self):
        """Constructor for Baseline4Player"""
        super().__init__()
        self.player_name = "Baseline4Player"
        self.inferences = []  # List of (color, positions) tuples
        self.tied_positions = {}  # Dictionary mapping positions to fixed colors
        self.being_fixed = None
        self.being_considered = None
        self.current_guess = None
        self.initialized = False

    def initialize_game(self, board_length: int, colors: List[str], scsa_name: str) -> None:
        """Initialize game state based on SCSA"""
        self.N = board_length
        self.colors = colors
        self.scsa_name = scsa_name
        
        self.tied_positions.clear()
        self.inferences.clear()
        
        if self.scsa_name == "ABColor":
            self.being_fixed = 'A'
            self.being_considered = 'B'
        else:
            self.being_fixed = colors[0]
            self.being_considered = colors[1]
            
        # Initialize position possibilities for each color
        for color in colors:
            positions = set(range(board_length))
            self.inferences.append((color, positions))
            
        self.initialized = True

    def make_guess(
        self,
        board_length: int,
        colors: list[str],
        scsa_name: str,
        last_response: tuple[int, int, int],
    ) -> str:
        """Makes a guess of the secret code for Mastermind

        Args:
            board_length (int): Number of pegs of secret code.
            colors (list[str]): All possible colors that can be used to generate a code.
            scsa_name (str): Name of SCSA used to generate secret code.
            last_response (tuple[int, int, int]): (exact matches, color matches, guess number)

        Returns:
            str: Next guess
        """
        # Initialize game if this is our first time or if parameters changed
        if not self.initialized:
            self.initialize_game(board_length, colors, scsa_name)
        
        # Unpack last response
        if last_response is None:
            # First guess
            self.current_guess = self.get_initial_guess()
            return self.current_guess
            
        bulls, cows, guess_number = last_response
        
        if bulls == board_length:
            return self.current_guess  # We've won!

        # Update our knowledge based on the last guess
        self.update_inferences(self.current_guess, bulls, cows)
        
        # Generate next guess
        self.current_guess = self.get_next()
        return self.current_guess

    def get_initial_guess(self) -> str:
        """Generate initial guess based on SCSA"""
        if self.scsa_name == "ABColor":
            # For ABColor, start with half A and half B
            half = self.N // 2
            return 'A' * half + 'B' * (self.N - half)
        elif self.scsa_name == "OnlyOnce":
            # For OnlyOnce, use each color once until running out of colors
            initial_colors = self.colors[:self.N]
            while len(initial_colors) < self.N:
                initial_colors.append(self.colors[0])
            return ''.join(initial_colors)
        else:
            # For InsertColors and others, start with all first color
            return self.colors[0] * self.N


    def get_next(self) -> str:
        """Generate next guess based on current inferences"""
        result = [''] * self.N
        
        # First, fill in all tied positions
        for pos, color in self.tied_positions.items():
            result[pos] = color

        # Fill remaining positions based on algorithm
        for i in range(self.N):
            if result[i]:  # Skip already filled positions
                continue
                
            if self.being_fixed and i == self.next_possible_position(self.being_fixed):
                result[i] = self.being_fixed
            elif len(self.inferences) == self.N:
                result[i] = self.second_unfixed()
            else:
                result[i] = self.being_considered

        return ''.join(result)

    def update_inferences(self, trial: str, bulls: int, cows: int) -> None:
        """Update inferences based on last guess response"""
        # Calculate gain
        if self.being_fixed is None:
            gain = bulls + cows - (self.num_fixed() - 1)
        else:
            gain = bulls + cows - self.num_fixed()

        # Handle different cases based on cows
        if cows == 0:
            if self.being_fixed:
                self.fix_color(self.being_fixed)
                self.bump_being_fixed()
        elif cows == 1:
            if self.being_fixed:
                self.delete_position_for_color(self.being_fixed, self.being_considered)
                self.delete_position_for_color(self.being_fixed, self.being_fixed)
        elif cows == 2:
            pos = self.next_possible_position(self.being_fixed)
            if pos >= 0:
                self.fix_color_in_position(self.being_considered, pos)

        # Add new inferences if there was a gain
        if gain > 0:
            self.add_lists(gain, self.being_considered)

        # Cleanup and get next color
        self.cleanup()
        self.next_color()

    # ... (helper methods from previous implementation remain the same) ...

    def cleanup(self) -> None:
        """Clean up inferences list"""
        fixed_positions = set()
        
        # Collect fixed positions
        for color, positions in self.inferences:
            if len(positions) == 1:
                fixed_positions.update(positions)
        
        # Remove fixed positions from other lists
        changed = True
        while changed:
            changed = False
            for color, positions in self.inferences:
                if len(positions) > 1:
                    original_len = len(positions)
                    positions.difference_update(fixed_positions)
                    if len(positions) != original_len:
                        changed = True
                    if len(positions) == 1:
                        fixed_positions.update(positions)

    def next_color(self) -> None:
        """Get next color for being_considered"""
        used_colors = {self.being_fixed}
        used_colors.update(self.tied_positions.values())
        
        available_colors = [c for c in self.colors if c not in used_colors]
        
        if not available_colors:
            self.being_considered = None
        else:
            self.being_considered = available_colors[0]
