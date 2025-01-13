import datetime
import pandas as pd
import numpy as np

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


def get_party_labels(data_transaction_labels: pd.DataFrame, data_party: pd.DataFrame) -> pd.DataFrame:
    """
    Assign SAR(Suspicious Activity Reports) labels to parties based on transaction data.

    Parameters:
    - data_transaction_labels (pd.DataFrame): DataFrame containing transaction labels, including SAR information.
    - data_party (pd.DataFrame): DataFrame with party information.

    Returns:
    pd.DataFrame: DataFrame with party labels indicating SAR occurrences.
    """
    alert_transactions = data_transaction_labels[data_transaction_labels.is_sar == 1]
    alert_sources = alert_transactions[["source", "tran_timestamp"]]
    alert_sources.columns = ["id", "tran_timestamp"]
    alert_targets = alert_transactions[["target", "tran_timestamp"]]
    alert_targets.columns = ["id", "tran_timestamp"]
    #sar_party = alert_sources.append(alert_targets, ignore_index=True)
    sar_party = pd.concat([alert_sources, alert_targets], ignore_index=True)

    sar_party.sort_values(["id", "tran_timestamp"], ascending=[False, True])

    # Find the first occurrence of SAR per ID
    sar_party = sar_party.iloc[[sar_party.id.eq(id).idxmax() for id in sar_party['id'].value_counts().index]]
    sar_party = sar_party.groupby([pd.Grouper(key='tran_timestamp', freq='M'), 'id']).agg(monthly_count=('id', 'count'))
    sar_party = sar_party.reset_index(level=["id"])
    sar_party = sar_party.reset_index(level=["tran_timestamp"])
    sar_party.drop(["monthly_count"], axis=1, inplace=True)

    sar_party["is_sar"] = sar_party["is_sar"] = 1

    party_labels = data_party.merge(sar_party, on=["id"], how="left")
    party_labels.is_sar = party_labels.is_sar.map({1.0: 1, np.nan: 0})
    max_time_stamp = datetime.datetime.utcfromtimestamp(int(max(data_transaction_labels.tran_timestamp.values)) / 1e9)
    party_labels = party_labels.fillna(max_time_stamp)

    return party_labels
