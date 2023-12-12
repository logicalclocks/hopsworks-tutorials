import numpy as np
import pandas as pd

def get_transaction_labels(data_transactions: pd.DataFrame, data_alert_transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Merge transaction data with alert transaction data to get labels indicating SAR occurrences.

    Parameters:
    - data_transactions (pd.DataFrame): DataFrame containing transaction information.
    - data_alert_transactions (pd.DataFrame): DataFrame with alert transaction information, including SAR labels.

    Returns:
    pd.DataFrame: Merged DataFrame with transaction labels indicating SAR occurrences.
    """
    transaction_labels = data_transactions[
        ["source", "target", "tran_id", "tran_timestamp"]
    ].merge(
        data_alert_transactions[["is_sar", "tran_id"]],
        on=["tran_id"],
        how="left",
    )
    transaction_labels.is_sar = transaction_labels.is_sar.map({
        True: 1,
        np.nan: 0,
    })
    transaction_labels.sort_values(
        'tran_id',
        inplace=True,
    )
    transaction_labels.rename(columns={"tran_id": "id"}, inplace=True)
    return transaction_labels