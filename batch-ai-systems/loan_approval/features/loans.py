import pandas as pd
import datetime
import numpy as np
from typing import Union

def zipcode(address: Union[str, int]) -> str:
    """
    Transform the address to a standardized zip code.

    Parameters:
    - address (str or int): The original zip code.

    Returns:
    - str: Standardized zip code (5 digits) or "0" if not a valid zip code.
    """
    # Convert the address to an integer
    zip_code = int(address)

    # Determine the length of the zip code
    l = len(str(zip_code))

    # Check if the length is 5, return the zip code as a string
    if l == 5:
        return str(zip_code)

    # Return "0" for invalid zip codes
    return "0"