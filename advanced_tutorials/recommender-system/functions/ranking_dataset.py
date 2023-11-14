import pandas as pd

def get_ranking_dataset(df, ds_type, feature_view_articles):
    
    def exclude_feat(s):
        return s.endswith("_id") or s.endswith("_no") or s.endswith("_code")
    
    DS_NAME = f"ranking_{ds_type}.csv"
    
    df['article_id'] = df['article_id'].astype(str)
    
    # These are the true positive pairs.
    query_features = ["customer_id", "age", "month_sin", "month_cos"]

    positive_pairs = df[query_features + ["article_id"]].copy()
    
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
    item_df = feature_view_articles.get_batch_data()
    item_df.drop_duplicates(subset="article_id", inplace=True)
    ranking_df = ranking_df.merge(item_df, on="article_id")
    
    # Compute the query and candidate embeddings
    # There are several "duplicated" categorical features in the dataset. 
    # For instance, `index_code` and `index_name` encodes the same feature, but in different formats (int, string). 
    # Therefore we have to deduplicate these features.

    features_to_exclude = [col for col in ranking_df.columns if exclude_feat(col)]
    features_to_exclude.append("prod_name")

    ranking_df.drop(features_to_exclude, axis="columns", inplace=True)
    
    return ranking_df