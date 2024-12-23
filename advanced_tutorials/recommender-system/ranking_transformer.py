
import logging

import hopsworks
import pandas as pd


class Transformer(object):
    def __init__(self):
        # Connect to Hopsworks
        project = hopsworks.login()
        self.fs = project.get_feature_store()

        # Retrieve 'transactions' feature group.
        self.transactions_fg = self.fs.get_feature_group("transactions", 1)

        # Retrieve the 'articles' feature view
        self.articles_fv = self.fs.get_feature_view(
            name="articles",
            version=1,
        )

        # Get list of feature names for articles
        self.articles_features = [feat.name for feat in self.articles_fv.schema]

        # Retrieve the 'customers' feature view
        self.customer_fv = self.fs.get_feature_view(
            name="customers",
            version=1,
        )

        self.customer_fv.init_serving(1)

        # Retrieve the 'candidate_embeddings' feature view
        self.candidate_index = self.fs.get_feature_view(
            name="candidate_embeddings",
            version=1,
        )

        # Retrieve ranking model
        mr = project.get_model_registry()
        model = mr.get_model(
            name="ranking_model",
            version=1,
        )

        self.ranking_fv = model.get_feature_view(init=False)
        self.ranking_fv.init_batch_scoring(1)

        # Get the names of features expected by the ranking model
        self.ranking_model_feature_names = [
            feature.name 
            for feature 
            in self.ranking_fv.schema 
            if feature.name != 'label'
        ]

    def preprocess(self, inputs):
        # Extract the input instance
        inputs = inputs["instances"][0]

        # Extract customer_id from inputs
        customer_id = inputs["customer_id"]

        # Search for candidate items
        neighbors = self.candidate_index.find_neighbors(
            inputs["query_emb"],
            k=100,
        )
        neighbors = [neighbor[0] for neighbor in neighbors]

        # Get IDs of items already bought by the customer
        already_bought_items_ids = (
            self.transactions_fg.select("article_id").filter(self.transactions_fg.customer_id==customer_id).read(dataframe_type="pandas").values.reshape(-1).tolist()
        )

        # Filter candidate items to exclude those already bought by the customer
        item_id_list = [
            str(item_id)
            for item_id in neighbors
            if str(item_id) not in already_bought_items_ids
        ]
        item_id_df = pd.DataFrame({"article_id": item_id_list})

        # Retrieve Article data for candidate items
        articles_data = [
            self.articles_fv.get_feature_vector({"article_id": item_id})
            for item_id in item_id_list
        ]

        logging.info("✅ Articles Data Retrieved!")

        articles_df = pd.DataFrame(
            data=articles_data,
            columns=self.articles_features,
        )

        # Join candidate items with their features
        ranking_model_inputs = item_id_df.merge(
            articles_df,
            on="article_id",
            how="inner",
        )

        logging.info("✅ Inputs are almost ready!")

        # Add customer features
        customer_features = self.customer_fv.get_feature_vector(
                {"customer_id": customer_id},
                return_type="pandas",
            )

        ranking_model_inputs["age"] = customer_features.age.values[0]
        ranking_model_inputs["month_sin"] = inputs["month_sin"]
        ranking_model_inputs["month_cos"] = inputs["month_cos"]

        # Select only the features required by the ranking model
        ranking_model_inputs = ranking_model_inputs[self.ranking_model_feature_names]

        logging.info("✅ Inputs are ready!")

        return {
            "inputs": [
                {
                    "ranking_features": ranking_model_inputs.values.tolist(),
                    "article_ids": item_id_list,
                }
            ]
        }

    def postprocess(self, outputs):
        logging.info("✅ Predictions are ready!")

        # Merge prediction scores and corresponding article IDs into a list of tuples
        ranking = list(zip(outputs["scores"], outputs["article_ids"]))

        # Sort the ranking list by score in descending order
        ranking.sort(reverse=True)

        # Return the sorted ranking list
        return {
            "ranking": ranking,
        }
