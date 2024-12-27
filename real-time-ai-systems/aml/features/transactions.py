import pandas as pd
import numpy as np

def get_out_transactions(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate monthly outgoing transaction statistics for each source ID.

    Parameters:
    - data (pd.DataFrame): DataFrame containing transaction information.

    Returns:
    pd.DataFrame: DataFrame with monthly outgoing transaction statistics.
    """
    out_df = data.groupby([pd.Grouper(key='tran_timestamp', freq='M'), 'source']) \
        .agg(monthly_count=('source', 'count'),
             monthly_total_amount=('base_amt', 'sum'),
             monthly_mean_amount=('base_amt', 'mean'),
             monthly_std_amount=('base_amt', 'std')
             )
    out_df = out_df.reset_index(level=["source"])
    out_df = out_df.reset_index(level=["tran_timestamp"])
    out_df.columns = ["tran_timestamp", "id", "monthly_out_count", "monthly_out_total_amount",
                      "monthly_out_mean_amount", "monthly_out_std_amount"]
    out_df.tran_timestamp = out_df.tran_timestamp.values.astype(np.int64) // 10 ** 6
    return out_df


def get_in_transactions(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate monthly incoming transaction statistics for each target ID.

    Parameters:
    - data (pd.DataFrame): DataFrame containing transaction information.

    Returns:
    pd.DataFrame: DataFrame with monthly incoming transaction statistics.
    """
    in_df = data.groupby([pd.Grouper(key='tran_timestamp', freq='M'), 'target']) \
        .agg(monthly_count=('target', 'count'),
             monthly_total_amount=('base_amt', 'sum'),
             monthly_mean_amount=('base_amt', 'mean'),
             monthly_std_amount=('base_amt', 'std'))

    in_df = in_df.reset_index(level=["target"])
    in_df = in_df.reset_index(level=["tran_timestamp"])
    in_df.columns = ["tran_timestamp", "id", "monthly_in_count", "monthly_in_total_amount",
                     "monthly_in_mean_amount", "monthly_in_std_amount"]
    in_df.tran_timestamp = in_df.tran_timestamp.values.astype(np.int64) // 10 ** 6
    return in_df


def get_in_out_transactions(data_transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Merge monthly incoming and outgoing transaction statistics.

    Parameters:
    - data_transactions (pd.DataFrame): DataFrame containing transaction information.

    Returns:
    pd.DataFrame: Merged DataFrame with monthly incoming and outgoing transaction statistics.
    """
    out_df = get_out_transactions(data_transactions)
    in_df = get_in_transactions(data_transactions)
    in_out_df = in_df.merge(out_df, on=['tran_timestamp', 'id'], how="outer")
    in_out_df = in_out_df.fillna(0)
    return in_out_df
