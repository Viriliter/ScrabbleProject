import random
import string
import re
import time
from pathlib import Path

from typing import List, Dict, Tuple, Any

from .globals import *

def generate_unique_id(length=8) ->str :
    """Generate a random ID consisting of letters and digits."""
    characters = string.ascii_letters + string.digits
    unique_id = ''.join(random.choice(characters) for _ in range(length))
    return unique_id

def serialize_dict(d: Dict[Any, Any]) -> Dict[str, Any]:
    r = {}
    for key, value in d.items():
        r[str(key)] = value
    return r

def verbalize(tiles: List[Tuple[LETTER, str, str]]) -> WORD:
    word: WORD = []
    for tile in tiles:
        letter = tile["letter"]
        location = tile["location"]

        match = re.match(r"([A-Z]+)(\d+)", location)
        if not match:
            return None  # Invalid format

        col_str, row_str = match.groups()
        c = sum((ord(char) - ord('A') + 1) * (26 ** i) for i, char in enumerate(reversed(col_str)))  # Convert 'A' -> 1, 'B' -> 2, ..., 'AA' -> 27
        r = int(row_str)
        
        letter = TILE(r, c, letter)
        word.append(letter)
        
    return word

def get_absolute_path(relative_path: str) -> str:
    parent_dir = Path(__file__).resolve().parent.parent
    absolute_path = (parent_dir / relative_path).resolve()

    return str(absolute_path)

def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter_ns()
        result = func(*args, **kwargs)
        elapsed_time = time.perf_counter_ns() - start_time
        print(f"{func.__name__} executed in {elapsed_time/10**3} microseconds")
        return result
    return wrapper