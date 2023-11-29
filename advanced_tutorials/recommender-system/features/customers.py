import pandas as pd

def fill_missing_club_member_status(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Fills missing values in 'club_member_status' with 'ABSENT'.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.

    Returns:
    - pd.DataFrame: DataFrame with missing values in 'club_member_status' filled.
    '''
    df['club_member_status'].fillna('ABSENT', inplace=True)
    return df


def drop_na_age(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Drops rows with missing values in the 'age' column.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.

    Returns:
    - pd.DataFrame: DataFrame with rows containing missing 'age' values removed.
    '''
    df.dropna(subset=['age'], inplace=True)
    return df


def create_age_group(df: pd.DataFrame) -> pd.Series:
    '''
    Creates a new column 'age_group' based on age bins.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing the 'age' column.

    Returns:
    - pd.Series: Series containing the 'age_group' for each row.
    '''
    age_bins = [0, 18, 25, 35, 45, 55, 65, 100]
    age_labels = ['0-18', '19-25', '26-35', '36-45', '46-55', '56-65', '66+']
    return pd.cut(df['age'], bins=age_bins, labels=age_labels)


def prepare_customers(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Prepares the input DataFrame by filling missing values, dropping rows with missing 'age',
    creating 'age_group' column, and dropping NaN values.

    Parameters:
    - df (pd.DataFrame): Input DataFrame.

    Returns:
    - pd.DataFrame: Processed DataFrame with new features and NaN values dropped.
    '''
    df = fill_missing_club_member_status(df)
    df = drop_na_age(df)
    df['age_group'] = create_age_group(df)
    df.dropna(axis=1, inplace=True)
    return df
