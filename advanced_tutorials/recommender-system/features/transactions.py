def prepare_transactions(df):
    df["article_id"] = df["article_id"].astype(str)
    df['t_dat'] = pd.to_datetime(df['t_dat'])
    df['year'] = df['t_dat'].dt.year
    df['month'] = df['t_dat'].dt.month
    df['day'] = df['t_dat'].dt.day
    df['day_of_week'] = df['t_dat'].dt.dayofweek

    # Calculate month_sin and month_cos in a vectorized way
    C = 2 * np.pi / 12
    df['month_sin'] = np.sin(df['month'] * C)
    df['month_cos'] = np.cos(df['month'] * C)
    
    # Convert python datetime object to unix epoch milliseconds 
    df['t_dat'] = df.t_dat.values.astype(np.int64) // 10 ** 6

    return df