def prepare_articles(df):
    df["article_id"] = df["article_id"].astype(str)
    df['prod_name_length'] = df['prod_name'].str.len()
    df['detail_desc_length'] = df['detail_desc'].str.len()
    df.dropna(axis=1, inplace=True)
    return df