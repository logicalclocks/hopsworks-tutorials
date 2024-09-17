from textblob import TextBlob
from word2number import w2n

def spell_check(text):
    """
    Checks and corrects the spelling of a given text.

    Parameters:
    - text (str): The text whose spelling is to be checked.

    Returns:
    - tuple: A tuple containing a boolean indicating if the original spelling was correct, and the corrected text.
    """
    # Convert the text to lower case to standardize it
    text_lower = text.lower()
    
    # Return early if the text is 'missing' or an empty string
    if text_lower in ['missing', ' ']:
        return False, 'missing'

    # Correct the text using TextBlob
    text_corrected = str(TextBlob(text_lower).correct())
    
    # Determine if the original text was spelled correctly
    spelling_is_correct = text_lower == text_corrected
    
    return spelling_is_correct, text_corrected.strip()


def amount_letter_number_match(amount_in_text_corrected, amount_in_number):
    """
    Compares the numeric value of a text representation of an amount to its numeric counterpart.

    Parameters:
    - amount_in_text_corrected (str): The text representation of an amount.
    - amount_in_number (str): The numeric representation of an amount.

    Returns:
    - bool or tuple: True if the amounts match, False otherwise, or a tuple with a message if data is missing.
    """
    # Handle missing values
    if 'missing' in [amount_in_text_corrected, amount_in_number]:
        return False, ('Amount in words is missing' if amount_in_text_corrected == 'missing' else 'Amount in numbers is missing')

    try:
        # Attempt to convert the textual representation to a number
        amount_text_to_num = w2n.word_to_num(amount_in_text_corrected)
        
        # Compare it to the provided numeric value, making sure to convert it to an int
        return amount_text_to_num == int(amount_in_number)
    
    # If Spell correction fails (for -> four)
    except Exception as e:
        return False

    
def get_amount_match_column(amount_in_text_corrected, amount_in_number):
    """
    Retrieves the match status or value for an amount, handling tuples indicating missing data.

    Parameters:
    - amount_in_text_corrected (str): The text representation of an amount, corrected for spelling.
    - amount_in_number (str): The numeric representation of an amount.

    Returns:
    - bool: True if the amounts match, False otherwise, or the first element of the tuple if an error message is present.
    """
    # Determine the match status or value
    match_value = amount_letter_number_match(
        amount_in_text_corrected, 
        amount_in_number,
    )
    
    # Return the value, handling tuple for error messages
    if isinstance(match_value, tuple):
        return match_value[0]
    
    return match_value
