def number_of_rows_per_key(df, key, column_name):
    data = df.groupby(key)[key].agg(['count'])
    data.columns = [column_name]
    return data


def clean_column(column_name):
    return column_name.lower().replace(' ', '_')


@transformer
def transform(df, *args, **kwargs):
    # Add number of meals for each user
    df_new_column = number_of_rows_per_key(df, 'user ID', 'number of meals')
    df = df.join(df_new_column, on='user ID')

    # Clean column names
    df.columns = [clean_column(col) for col in df.columns]

    return df.iloc[:100]


@test
def test_number_of_columns(df, *args) -> None:
    assert len(df.columns) >= 11, 'There needs to be at least 11 columns.'