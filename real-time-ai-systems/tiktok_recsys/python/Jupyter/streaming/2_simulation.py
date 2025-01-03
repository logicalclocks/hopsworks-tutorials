import json
import sys
sys.path.insert(1, '../')

import pandas as pd
from tqdm import tqdm
import hopsworks
from confluent_kafka import Producer

import config
from utils.hsfs_bytewax import get_kafka_config
from features.users import generate_users
from features.videos import generate_video_content
from features.interactions import generate_interactions

def simulate_interactions():
    # Generate data for users
    user_data = generate_users(config.USERS_AMOUNT_PIPELINE)
    data_users_df = pd.DataFrame(user_data)

    # Generate data for videos
    video_data = generate_video_content(config.VIDEO_AMOUNT_PIPELINE)
    data_video_df = pd.DataFrame(video_data)

    # Generate interactions
    interactions = generate_interactions(
        config.INTERACTIONS_AMOUNT_PIPELINE, 
        user_data, 
        video_data,
    )
    data_interactions_df = pd.DataFrame(interactions)
    
    data_interactions_df['json'] = data_interactions_df.apply(lambda x: x.to_json(), axis=1)
    
    return [json.loads(i) for i in data_interactions_df.json.values]
    

# Connect to Hopsworks
project = hopsworks.login()
fs = project.get_feature_store()

kafka_api = project.get_kafka_api()
kafka_config = get_kafka_config(fs.id)

print(kafka_config)
producer = Producer(kafka_config)

# Simulate interactions
interactions_data = simulate_interactions()

# Send to source topic
for interaction in tqdm(interactions_data, desc="Sending messages"):
    producer.produce(
        config.KAFKA_TOPIC_NAME,
        json.dumps(interaction)
    )
    producer.flush()
