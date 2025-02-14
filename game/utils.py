import random
import string
import re

from typing import List, Dict, Tuple

from .globals import *

def generate_unique_id(length=8) ->str :
    """Generate a random ID consisting of letters and digits."""
    characters = string.ascii_letters + string.digits
    unique_id = ''.join(random.choice(characters) for _ in range(length))
    return unique_id

#'id': tileID, 'value': letter, 'loc': location, 'isJoker': isJoker
def verbalize(tiles: Dict[str, Tuple[chr, str, str]]) -> WORD:
    word: WORD = []
    for id, properties in tiles.items():
        letter = properties["letter"]
        loc = properties["loc"]

        match = re.match(r"([A-Z]+)(\d+)", loc)
        if not match:
            return None  # Invalid format

        col_str, row_str = match.groups()
        c = sum((ord(char) - ord('A') + 1) * (26 ** i) for i, char in enumerate(reversed(col_str)))  # Convert 'A' -> 1, 'B' -> 2, ..., 'AA' -> 27
        r = int(row_str)
        
        letter = LETTER(r, c, letter)
        word.append(letter)
        
    return word