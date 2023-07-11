import pandas as pd
import numpy as np


###########################################################################################

def shift_pm_2_5(df, days=5):
    for shift_value in range(1, days + 1):
        df[f'pm_2_5_previous_{shift_value}_day'] = df.groupby('city_name')['pm2_5'].shift(shift_value)
    df = df.dropna()


def moving_average(df, window=7):
    df[f'mean_{window}_days'] = df.groupby('city_name')['pm2_5'] \
                                    .rolling(window=window).mean().reset_index(0,drop=True).shift(1)


def moving_std(df, window):
    df[f'std_{window}_days'] = df.groupby('city_name')['pm2_5'] \
                                    .rolling(window=window).std().reset_index(0,drop=True).shift(1)


def exponential_moving_average(df, window):
    df[f'exp_mean_{window}_days'] = df.groupby('city_name')['pm2_5'].ewm(span=window) \
                                        .mean().reset_index(0,drop=True).shift(1)


def exponential_moving_std(df, window):
    df[f'exp_std_{window}_days'] = df.groupby('city_name')['pm2_5'].ewm(span=window) \
                                        .std().reset_index(0,drop=True).shift(1)
    
    
###########################################################################################

def year(df):
    # Extract year, month, and day of the week from the 'date' column
    df['year'] = df['date'].dt.year.astype(int)


def day_of_month(df):
    df['day_of_month'] = df['date'].dt.day.astype(int)


def month(df):
    df['month'] = df['date'].dt.month.astype(int)


def day_of_week(df):
    df['day_of_week'] = df['date'].dt.dayofweek.astype(int)


def is_weekend(df):
    df['is_weekend'] = np.where(df['day_of_week'].isin([5,6]), 1, 0)


def sin_day_of_year(df):
    day_of_year = df['date'].dt.dayofyear
    df['sin_day_of_year'] = np.sin(2 * np.pi * day_of_year / 365)


def cos_day_of_year(df):
    day_of_year = df['date'].dt.dayofyear
    df['cos_day_of_year'] = np.cos(2 * np.pi * day_of_year / 365)


def sin_day_of_week(df):
    df['sin_day_of_week'] = np.sin(2 * np.pi * df['day_of_week'] / 7)


def cos_day_of_week(df):
    df['cos_day_of_week'] = np.cos(2 * np.pi * df['day_of_week'] / 7)


def feature_engineer_aq(df):
    df_res = df.copy()
    shift_pm_2_5(df_res, days=7) # add features about 7 previous PM2.5 values

    moving_average(df_res, 7)
    moving_average(df_res, 14)
    moving_average(df_res, 28)

    for i in [7, 14, 28]:
        for func in [moving_std,
                     exponential_moving_average,
                     exponential_moving_std
                     ]:
            func(df_res, i)


    df_res = df_res.sort_values(by=["date", "pm2_5"]).dropna()
    df_res = df_res.reset_index(drop=True)

    year(df_res)
    day_of_month(df_res)
    month(df_res)
    day_of_week(df_res)
    is_weekend(df_res)
    sin_day_of_year(df_res)
    cos_day_of_year(df_res)
    sin_day_of_week(df_res)
    cos_day_of_week(df_res)
    return df_res
