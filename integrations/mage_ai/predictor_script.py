import os
import numpy as np
import hsfs
import joblib


class Predict(object):

    def __init__(self):
        """ Initializes the serving state, reads a trained model"""        
        # Get feature store handle
        fs_conn = hsfs.connection()
        self.fs = fs_conn.get_feature_store()
        
        # Get feature view
        self.fv = self.fs.get_feature_view("transactions_view", 1)
        
        # Initialize serving
        self.fv.init_serving(1)

        # Load the trained model
        self.model = joblib.load(os.environ["ARTIFACT_FILES_PATH"] + "/xgboost_model.pkl")
        print("Initialization Complete")

    def predict(self, inputs):
        """ Serves a prediction request usign a trained model"""
        feature_vector = self.fv.get_feature_vector({"cc_num": inputs[0][0]})
        feature_vector = feature_vector[:-1]
        
        return self.model.predict(np.asarray(feature_vector).reshape(1, -1)).tolist() # Numpy Arrays are not JSON serializable
