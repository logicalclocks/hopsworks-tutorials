import pandas as pd
import numpy as np


def remove_nans(df):
    '''
    Function which removes missing values.
    If column has more than 20% of missing values -> remove.
    The rest missing values will be dropped by rows.
    
    Args:
    -----
    df: pd.DataFrame
        DataFrame in which all missing values will be deleted.
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with no missing values.
    
    '''
    nan_df = df.isna().sum()[df.isna().sum() > 0]
    nan_perc = (nan_df / df.shape[0] * 100).apply(int)
    cols_to_drop = nan_perc[nan_perc >= 20].index
    df = df.drop(cols_to_drop, axis = 1).dropna()
    return df


def get_subsample(df):
    '''
    Function which randomly selects 25% of input data
    
    Args:
    -----
    df: pd.DataFrame
        DataFrame from which we will get 25% subsample.
        
    Returns:
    --------
    pd.DataFrame
        25% of original DataFrame.
    
    '''
    indexes = np.random.choice(df.index, int(df.shape[0] * 0.25), replace = False)
    return df.loc[indexes].reset_index(drop = True)


def add_perc(ax, feature, Number_of_categories, hue_categories):
    '''
    Function which adds percentages grouped by hue column to the top of bars.
    
    Args:
    ----
    ax: matplotlib.axes
        Ax with plot.
    feature: pd.Series
        X axis feature.   
    Number_of_categories: int
        Number of unique categories of X axis feature.    
    hue_categories: int:
         Number of unique categories of hue feature.
    
    Returns:
    --------
    matplotlib.axes
        Annotated ax.
    
    '''
    a = [p.get_height() for p in ax.patches]
    patch = [p for p in ax.patches]
    for i in range(Number_of_categories):
        total = feature.value_counts().values[i]
        for j in range(hue_categories):
            percentage = '{:.1f}%'.format(100 * a[(j*Number_of_categories + i)]/total)
            x = patch[(j*Number_of_categories + i)].get_x() + patch[(j*Number_of_categories + i)].get_width() / 2 - 0.15
            y = patch[(j*Number_of_categories + i)].get_y() + patch[(j*Number_of_categories + i)].get_height()
            ax.annotate(percentage, (x, y+1500), size = 12)


def generate_value(col_values:pd.Series):
    '''
    Function which returns a random value which is generated using probabilities of each value occurrence.

    Args:
    -----
    col_values: pd.Series
        A column on which we will generate a value.

    Returns:
    --------
        A generated random value.

    '''
    value_counts = col_values.value_counts()
    value_probabilities = value_counts / col_values.shape[0]
    values = value_counts.index
    return np.random.choice(
        a=values,
        p=value_probabilities
    )


def generate_observation(data:pd.DataFrame)->list:
    '''
    Function which generates a row of a dataframe.

    Args:
    -----
    data: pd.DataFrame
        A dataset that will be used to generate new observations.

    Returns:
    --------
        A list of generates values for each column (new row of a dataframe).
    '''
    return [generate_value(data[column]) for column in data]


def generate_data(data:pd.DataFrame,amount:int=10)->pd.DataFrame:
    '''
    Generates a new DataFrame depending on existing DataFrame's column values probabilities.

    Args:
    -----
    data: pd.DataFrame
        A dataset that will be used to generate new observations.
    amount: int 
        Amount on generated rows.
        Default: 10

    Returns:
    --------
    pd.DataFrame
        Generated DataFrame.
    '''
    pk_existing = [pk for pk in data.columns if pk in ['sk_id_prev','sk_id_curr','sk_id_bureau']]
    pk_max = data[pk_existing].agg({'max'}).values[0]
    
    df = pd.DataFrame(
        [[*[pk + i for pk in pk_max],*generate_observation(data.drop(pk_existing,axis=1))] for i in range(amount)],
        columns=data.columns
    )
    df = df.dropna()
    return df
