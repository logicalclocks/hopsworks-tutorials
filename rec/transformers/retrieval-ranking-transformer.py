import hsfs

class Ranking(Transformer):
    def __init__(self):
      connection = hsfs.connect(...)
      fs = connect()
      fv_articles = fs.get_feature_view(“articles”, version=1)
      fv_ranking = fs.get_feature_view(“ranking”, version=1)

    def remove_row(articles, article_id):
        articles = articles.remove(article_id)


    def preprocess(self, inputs):
        """The object returned will be used as model input."""
        customer_id = inputs[...]
        user_query_embedding = inputs[...]

        # ANN lookup of candidates
        candidates = opensearch.read(user_query_embedding)

        # get all article-ids for candidates
        article_ids = []
        for c in candidates:
           article_ids.add(c.article_id)

        article_ids_commas = ",".join(article_ids)

# https://examples.hopsworks.ai/master/featurestore/hsfs/basics/feature_exploration/ 
# returns a dataframe ‘already_bought’
        df_already_bought = fs.sql(“select article_id from user_purchases where id = ” + customer_id + “ AND article_id IN (“ + article_ids_commas)

  # Remove already bought items
  df_already_bought.apply(lambda row :
remove_row(row['article_id']), axis = 1)
          
        # Batch lookup of features for articles
        # TODO: Davit Bzhalava - what’s the correct syntax?
        article_features_array = fv_articles.get_feature_vector(
batch=article_ids)

        # batch prediction with the model
        inputs = inputs + article_features_array

        return inputs

    def postprocess(self, outputs):

        outputs = reorder_based_on_ranking_scores(outputs)

        return outputs


