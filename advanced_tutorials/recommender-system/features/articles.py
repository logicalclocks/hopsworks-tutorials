import pandas as pd

def get_article_id(df: pd.DataFrame) -> pd.Series:
    '''
    Extracts and returns the article_id column as a string.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing the 'article_id' column.

    Returns:
    - pd.Series: Series containing the 'article_id' column as strings.
    '''
    return df["article_id"].astype(str)


def create_prod_name_length(df: pd.DataFrame) -> pd.Series:
    '''
    Creates a new column 'prod_name_length' representing the length of 'prod_name'.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing the 'prod_name' column.

    Returns:
    - pd.Series: Series containing the length of 'prod_name' for each row.
    '''
    return df['prod_name'].str.len()


def create_detail_desc_length(df: pd.DataFrame) -> pd.Series:
    '''
    Creates a new column 'detail_desc_length' representing the length of 'detail_desc'.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing the 'detail_desc' column.

    Returns:
    - pd.Series: Series containing the length of 'detail_desc' for each row.
    '''
    return df['detail_desc'].str.len()


def prepare_articles(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Prepares the input DataFrame by creating new features and dropping NaN values.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.

    Returns:
    - pd.DataFrame: Processed DataFrame with new features and NaN values dropped.
    '''
    df["article_id"] = get_article_id(df)
    df['prod_name_length'] = create_prod_name_length(df)
    df['detail_desc_length'] = create_detail_desc_length(df)
    df.dropna(axis=1, inplace=True)
    return df
