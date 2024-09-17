import pandas as pd

def compute_ranking_dataset(trans_fg, articles_fg, customers_fg):
    
    query_features = ["customer_id", "age", "month_sin", "month_cos", "article_id"]
    
    fg_query = trans_fg.select(["month_sin", "month_cos"]).join(articles_fg.select_all(), on=["article_id"]).join(customers_fg.select(["customer_id", "age"]))
    df = fg_query.read()
    df = df[query_features]

    positive_pairs = df.copy()
    
    n_neg = len(positive_pairs)*10

    negative_pairs = positive_pairs[query_features]\
        .sample(n_neg, replace=True, random_state=1)\
        .reset_index(drop=True)

    negative_pairs["article_id"] = positive_pairs["article_id"]\
        .sample(n_neg, replace=True, random_state=2).to_numpy() 
    
    # Add labels.
    positive_pairs["label"] = 1
    negative_pairs["label"] = 0

    # Concatenate.
    ranking_df = pd.concat([positive_pairs, negative_pairs], ignore_index=True)
    
    # Merge with item features.
    item_df = articles_fg.read()
    item_df.drop_duplicates(subset="article_id", inplace=True)
    ranking_df = ranking_df.merge(item_df, on="article_id")
    
    # Compute the query and candidate embeddings
    # There are several "duplicated" categorical features in the dataset. 
    # For instance, `index_code` and `index_name` encodes the same feature, but in different formats (int, string). 
    # Therefore we have to deduplicate these features.
    ranking_df = ranking_df[["customer_id", "article_id", "age","month_sin", "month_cos", "product_type_name", "product_group_name", "graphical_appearance_name", "colour_group_name", "perceived_colour_value_name", 
                             "perceived_colour_master_name","department_name", "index_name", "index_group_name","section_name", "garment_group_name", "label"]]
    
    return ranking_df
