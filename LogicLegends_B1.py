"""
Below is the implementation of a Player class using the baseline strategy B2 from the Project Description:

B2: Exhaustively enumerate all possibilities. Guess each possibility in lexicographic order unless it was ruled out
by some previous response. For example, for p = 4, if guess AAAB got 0 1 1 in response, you would never again
on that round make any guess that began with AAA or ended in B.

"""

import time
import random
from player import *
from itertools import product


class Baseline1(Player):
    