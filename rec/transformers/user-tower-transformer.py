import hsml
import hsfs

class UserTower(Transformer):
    def __init__(self):
        connection = hsfs.connect(...)
        fs = connect()
        fv = fs.get_feature_view(“customers”, version=1)
   m_connection = hsml.connect(...)
        ranking_server = s.get_deployment("ranking-retrieval")

    def preprocess(self, inputs):
        """The object returned will be used as model input."""
        customer_id = inputs[]
        user_features =  fv.get_feature_vector(
            { “customer_id” : customer_id }
        )
        inputs[] = 

        return inputs # Sent to the UserTower embedding model

    def postprocess(self, outputs):
        """Transform the predictions computed by the model before returning a response."""
	   outputs = ranking_server.predict(outputs)

        return outputs

