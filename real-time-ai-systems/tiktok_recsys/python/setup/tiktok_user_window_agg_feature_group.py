import hopsworks

from hsfs.feature import Feature
from datetime import datetime, timedelta, timezone

project = hopsworks.login()
fs = project.get_feature_store()

features = [
    Feature(name="user_id", type="bigint"),
    Feature(name="category_id", type="bigint"),

    Feature(name="like_count", type="bigint"),
    Feature(name="dislike_count", type="bigint"),
    Feature(name="view_count", type="bigint"),
    Feature(name="comment_count", type="bigint"),
    Feature(name="share_count", type="bigint"),
    Feature(name="skip_count", type="bigint"),
    Feature(name="total_watch_time", type="bigint"),

    Feature(name="interaction_month", type="string"),
    Feature(name="window_end_time", type="timestamp"),
]

user_window_agg_1h_fg = fs.create_feature_group(
    "user_window_agg_1h",
    version=1,
    statistics_config=False,
    primary_key=["user_id"],
    partition_key=["interaction_month"],
    event_time="window_end_time",
    online_enabled=True,
    stream=True,
)

user_window_agg_1h_fg.save(features)


feature_descriptions = [
    {"name": "user_id", "description": "Unique identifier for each user."},
    {"name": "category_id", "description": "Id of the video category."},
    {"name": "window_end_time", "description": "End of the specified time window where interaction were aggregated."},
    {"name": "interaction_month",
     "description": "Month of the end of the specified time window where interaction were aggregated. Derived from window_end_time"},
    {"name": "like_count",
     "description": "Number of likes video category got from the user during a specified time window."},
    {"name": "dislike_count",
     "description": "Number of dislikes video category got from the user during a specified time window."},
    {"name": "view_count",
     "description": "Number of views over video category got from the user during a specified time window."},
    {"name": "comment_count",
     "description": "Number of comments video category got from the user during a specified time window."},
    {"name": "share_count",
     "description": "Number of likes over video category got from the user during a specified time window."},
    {"name": "skip_count",
     "description": "Number of times video category was skiped by the user during a specified time window."},
    {"name": "total_watch_time",
     "description": "Total time in seconds video category was watched by the user during a specified time window."},
]

for desc in feature_descriptions:
    user_window_agg_1h_fg.update_feature_description(desc["name"], desc["description"])

# user_window_agg_1h_fg.materialization_job.schedule(cron_expression="0 */15 * ? * *", start_time=datetime.now(tz=timezone.utc))
