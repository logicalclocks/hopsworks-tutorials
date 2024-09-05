# Setup the feature groups for the Flink pipelines
import pandas as pd
import hopsworks
from hsfs.feature import Feature
from datetime import datetime, timedelta, timezone

project = hopsworks.login()
fs = project.get_feature_store()

features = [
    Feature(name="interaction_month", type="string"),
    Feature(name="id", type="bigint"),
    Feature(name="user_id", type="bigint"),
    Feature(name="video_id", type="bigint"),
    Feature(name="category_id", type="bigint"),
    Feature(name="interaction_type", type="string"),
    Feature(name="watch_time", type="bigint"),
    Feature(name="interaction_date", type="timestamp"),
]

interactions_fg = fs.get_or_create_feature_group(
    name="interactions",
    description="Interactions data.",
    version=1,
    primary_key=["id"],
    partition_key=["interaction_month"],
    online_enabled=True,
    event_time="interaction_date"

)

interactions_fg.save(features)

feature_descriptions = [
    {"name": "id", "description": "Unique id for the interaction"},
    {"name": "user_id", "description": "Unique identifier for each user."},
    {"name": "video_id", "description": "Identifier for the video."},
    {"name": "category_id", "description": "Id of the video category."},
    {"name": "interaction_type", "description": "Type of interaction"},
    {"name": "watch_time", "description": "Time in seconds how long user watched the video."},
    {"name": "interaction_date", "description": "Date of inteaction."},
    {"name": "interaction_month", "description": "Month of interaction, derived from interaction_date."}
]

for desc in feature_descriptions:
    interactions_fg.update_feature_description(desc["name"], desc["description"])

# interactions_fg.materialization_job.schedule(cron_expression="0 */15 * ? * *", start_time=datetime.now(tz=timezone.utc))
