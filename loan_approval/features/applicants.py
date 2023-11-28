import pandas as pd
import datetime
import numpy as np
from typing import Union

def home_ownership(home_ownership: str) -> str:
    """
    Transform the home ownership status.

    Parameters:
    - home_ownership (str): The original home ownership status.

    Returns:
    - str: Transformed home ownership status.
    """
    if (home_ownership == 'ANY' or home_ownership == 'NONE'):
        return 'OTHER'
    return home_ownership


def pub_rec(number: float) -> int:
    """
    Transform the public record number.

    Parameters:
    - number (float): The original public record number.

    Returns:
    - int: Transformed public record number (0 or 1).
    """
    if number == 0.0:
        return 0
    else:
        return 1


def mort_acc(number: float) -> Union[int, float]:
    """
    Transform the mortgage account number.

    Parameters:
    - number (float): The original mortgage account number.

    Returns:
    - Union[int, float]: Transformed mortgage account number (0, 1, or the original number).
    """
    if number == 0.0:
        return 0
    elif number >= 1.0:
        return 1
    else:
        return number


def pub_rec_bankruptcies(number: float) -> Union[int, float]:
    """
    Transform the public record bankruptcies number.

    Parameters:
    - number (float): The original public record bankruptcies number.

    Returns:
    - Union[int, float]: Transformed public record bankruptcies number (0, 1, or the original number).
    """
    if number == 0.0:
        return 0
    elif number >= 1.0:
        return 1
    else:
        return number


def fill_mort_acc(total_acc: float, mort_acc: float, total_acc_avg: pd.Series) -> float:
    """
    Fill missing values in mortgage account based on total account average.

    Parameters:
    - total_acc (float): Total account number.
    - mort_acc (float): Original mortgage account number.
    - total_acc_avg (pd.Series): Average mortgage account number based on total account.

    Returns:
    - float: Filled mortgage account number.
    """
    if np.isnan(mort_acc):
        return total_acc_avg[total_acc].round()
    else:
        return mort_acc


def earliest_cr_line(earliest_cr_line: datetime.date) -> int:
    """
    Transform the earliest credit line date to the year.

    Parameters:
    - earliest_cr_line (datetime.date): The original earliest credit line date.

    Returns:
    - int: The year of the earliest credit line.
    """
    return earliest_cr_line.year


def mean_mort_acc(applicants_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the mean mortgage account number grouped by total account.

    Parameters:
    - applicants_df (pd.DataFrame): DataFrame containing applicant data.

    Returns:
    - pd.DataFrame: DataFrame with the mean mortgage account number.
    """
    result = applicants_df.groupby('total_acc')['mort_acc'].mean().reset_index()
    return result.rename(columns={'mort_acc': 'mean_mort_acc'})
