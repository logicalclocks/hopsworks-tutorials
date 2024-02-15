
import os
import hsfs
import numpy as np
import tensorflow as tf

class Transformer(object):
    
    def __init__(self):        
        # Get feature store handle
        fs_conn = hsfs.connection()
        self.fs = fs_conn.get_feature_store()
        
        # Get feature views
        self.fv = self.fs.get_feature_view(
            name="aml_feature_view", 
            version=1,
        )
        
        # Initialise serving
        self.fv.init_serving(1)
    
    def preprocess(self, inputs):
        # Retrieve feature vector using the feature vector provider
        feature_vector = self.fv.get_feature_vector({"id": inputs["inputs"][0]})

        # Explode embeddings (flatten the list of embeddings)
        feature_vector_exploded_emb = [*self.flat2gen(feature_vector)]

        # Reshape feature vector to match the model's input shape
        feature_vector_reshaped = np.array(feature_vector_exploded_emb).reshape(1, 41)

        # Convert the feature vector to a TensorFlow constant
        input_vector = tf.constant(feature_vector_reshaped, dtype=tf.float32)

        # Add a time dimension (axis=1) to the input vector
        input_vector = tf.expand_dims(input_vector, axis=1)

        # Duplicate the input vector to create a pair
        input_vector = tf.tile(input_vector, [1, 2, 1])
        
        # Duplicate the input vector to create a pair
        input_vector = input_vector.numpy().tolist()

        # Return the preprocessed input dictionary
        return {
            'inputs': input_vector
        }

    def postprocess(self, outputs):
        return outputs

    def flat2gen(self, alist):
        for item in alist:
            if isinstance(item, list):
                for subitem in item: yield subitem
            else:
                yield item 
