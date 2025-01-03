import pandas as pd
from typing import List

def split_page(document: str) -> List[str]:
    """
    Splits a document into a list of paragraphs based on newline characters.

    Parameters:
    - document (str): The input document to be split.

    Returns:
    - List[str]: A list of paragraphs.
    """
    return document.split('\n \n')


def get_paragraphs(data: pd.DataFrame) -> pd.DataFrame:
    """
    Explodes the 'text' column in the DataFrame, adds a 'paragraph' column indicating the index
    of the element in the list grouped by file_name and page_number.

    Parameters:
    - data (pd.DataFrame): The input DataFrame containing 'file_name', 'page_number', and 'text' columns.

    Returns:
    - pd.DataFrame: The modified DataFrame with an added 'paragraph' column.
    """
    # Explode the list to separate rows
    data_text_exploded = data.explode('text')

    # Add a 'paragraph' column indicating the index of the element in the list
    data_text_exploded['paragraph'] = data_text_exploded.groupby(
        ['file_name', 'page_number']
    ).cumcount() + 1

    return data_text_exploded


def process_text_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processes text data by applying the split_page, get_paragraphs functions.

    Parameters:
    - df (pd.DataFrame): The input DataFrame containing 'file_name' and 'text' columns.

    Returns:
    - pd.DataFrame: The processed DataFrame with 'file_name', 'page_number', 'paragraph', and 'text' columns.
    """
    # Apply split_page function to split text into paragraphs
    df['text'] = df['text'].apply(split_page)

    # Apply get_paragraphs function to explode the list and add paragraph numbers
    df = get_paragraphs(df)

    # Apply strip to remove leading and trailing spaces
    df['text'] = df['text'].str.strip()

    # Filter rows where the length of the 'text' column is greater than 500
    df = df[df['text'].str.len() > 500]

    # Set a regex pattern to identify rows with 5 or more consecutive dots or dashes
    pattern_to_remove = r'(\.{5,}|\-{5,})'

    # Remove rows matching the pattern
    df_filtered = df[~df['text'].str.contains(pattern_to_remove, regex=True)]

    # Reset index
    df_filtered.reset_index(drop=True, inplace=True)

    # Reorder columns for better readability
    df_filtered = df_filtered[['file_name', 'file_link', 'page_number', 'paragraph', 'text']]

    return df_filtered
