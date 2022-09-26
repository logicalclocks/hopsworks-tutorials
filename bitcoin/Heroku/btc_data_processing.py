import pandas as pd
import numpy as np
import datetime


def moving_average(df,window = 7):
    df[f'mean_{window}_days'] = df['close'].rolling(window = window).mean()
    return df

def moving_std(df,window):
    df[f'std_{window}_days'] = df.close.rolling(window = window).std()
    return df

def exponential_moving_average(df, window):
    df[f'exp_mean_{window}_days'] = df.close.ewm(span = window).mean()
    return df

def exponential_moving_std(df, window):
    df[f'exp_std_{window}_days'] = df.close.ewm(span = window).std()
    return df

def momentum_price(df,window):
    '''
     It is the rate of acceleration of a security's price or volume; the speed at which the price is changing.
    '''
    df[f'momentum_{window}_days'] = df.close.diff(window)
    return df

def rate_of_change(df,window):
    '''
     Assets with higher ROC values are considered more likely to be overbought;Lower - likely to be oversold.
    '''
    M = df.close.diff(window - 1)
    N = df.close.shift(window - 1)
    df[f'rate_of_change_{window}_days'] = (M / N) * 100
    return df

def strength_index(df, period):
    '''
     It is a momentum indicator that measures the magnitude of recent price changes
     to evaluate overbought or oversold conditions in the price of a stock or other asset.
     Ranging from [0,100].
     Asset -> 70: asset deemed overbought.
     Asset -> 30: asset getting undersold & undervalued.
    '''
    delta = df.close.diff().dropna()
    u = delta * 0
    d = u.copy()
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    u[u.index[period-1]] = np.mean( u[:period] )
    u = u.drop(u.index[:(period-1)])
    d[d.index[period-1]] = np.mean( d[:period] )
    d = d.drop(d.index[:(period-1)])
    rs = u.ewm(com = period-1, adjust = False).mean() / d.ewm(com = period-1, adjust = False).mean()
    df[f'strength_index_{period}_days'] = 100 - 100 / (1 + rs)
    return df

def process_btc_data(df):
    df = moving_average(df,7)
    df = moving_average(df,14)
    df = moving_average(df,56).fillna(0)

    df['signal'] = np.where(df['mean_7_days'] > df['mean_56_days'], 1.0, 0.0)

    for i in [7, 14, 56]:
        for func in [moving_std, exponential_moving_average,
                     exponential_moving_std,
                     momentum_price, rate_of_change,
                     strength_index]:
            df = func(df, i).fillna(0)

    df["date"] = df["date"].astype(str)
    return df
