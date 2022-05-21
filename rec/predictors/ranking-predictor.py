class RankingPredictor(object):

    def __init__(self):
        """ Initializes the serving state, reads a model from HDFS"""
# Env var ARTIFACT_FILES_PATH has the path to the model artifact files

      self.model = joblib.load(os.environ["ARTIFACT_FILES_PATH"] + "/user-query-embedding.pkl")



    def predict(self, inputs):
        """ Serves a prediction request usign a trained model"""
        return self.model.predict(inputs) 



    def classify(self, inputs):
        """ Serves a classification request using a trained model"""
        return "not implemented"

    def regress(self, inputs):
        """ Serves a regression request using a trained model"""
        return "not implemented"

