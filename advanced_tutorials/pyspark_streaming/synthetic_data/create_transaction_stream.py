import init_kafka
import synthetic_data
import hsfs
from hsfs.core.storage_connector_api import StorageConnectorApi
from confluent_kafka import Producer

# creating kafka topic and schema
init_kafka.init() 

# Creating simulated data
data_simulater = synthetic_data.synthetic_data()
credit_cards, trans_df = data_simulater.create_simulated_transactions()
#TODO : Remove and make this into a different dataframe
trans_df = trans_df.drop(["fraud_label"], axis = 1)

# Getting Kafka Configurations
connection = hsfs.connection()
fs = connection.get_feature_store()
sc_api = StorageConnectorApi()
sc = sc_api.get_kafka_connector(fs.id, False)

kafka_config = sc.confluent_options()
kafka_config["group.id"] = "test_groupid"

producer = Producer(kafka_config)

for index, transaction in trans_df.iterrows():
    producer.produce(init_kafka.KAFKA_TOPIC_NAME, transaction.to_json())
    producer.flush() # Synchronising read and write blocking call
    if index % 100 == 0 :
        print(f'index {index}')

