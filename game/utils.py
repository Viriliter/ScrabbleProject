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
    """
    @brief Convert a dictionary with non-string keys to a dictionary with string keys.
    @param d: The dictionary to be serialized.
    @return: A new dictionary with string keys.
    """
    r = {}
    for key, value in d.items():
        r[str(key)] = value
    return r

def verbalize(tiles: List[Tuple[LETTER, str, str]]) -> WORD:
    """
    @brief Convert a list of tiles into a WORD object.
    @param tiles: A list of tuples containing the letter, row, and column.
    @return: A WORD object representing the tiles.
    """
    word: WORD = []
    for tile in tiles:
        letter = tile["letter"]
        location = tile["location"]

        match = re.match(r"([A-Z]+)(\d+)", location)
        if not match:
            return None  # Invalid format

        col_str, row_str = match.groups()
        c = sum((ord(char) - ord('A')) * (26 ** i) for i, char in enumerate(reversed(col_str)))  # Convert 'A' -> 1, 'B' -> 2, ..., 'AA' -> 27
        r = int(row_str) - 1
        
        letter = TILE(r, c, letter)
        word.append(letter)
        
    return word

def get_absolute_path(relative_path: str) -> str:
    """
    @brief Get the absolute path of a file relative to the current script.
    @param relative_path: The relative path to the file.
    @return: The absolute path of the file.
    """
    parent_dir = Path(__file__).resolve().parent.parent
    absolute_path = (parent_dir / relative_path).resolve()

    return str(absolute_path)

def measure_time(func):
    """
    @brief Decorator to measure the execution time of a function.
    @param func: The function to be decorated.
    @return: A wrapper function that measures the execution time.
    """
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter_ns()
        result = func(*args, **kwargs)
        elapsed_time = time.perf_counter_ns() - start_time
        print(f"{func.__name__} executed in {elapsed_time/10**3} microseconds")
        return result
    return wrapper