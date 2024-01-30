import hopsworks

from hsfs.feature import Feature

project = hopsworks.login()
fs = project.get_feature_store()

features = [
    Feature(name="ride_id", type="string"),
    Feature(name="ride_status", type="string"),
    Feature(name="point_idx", type="int"),
    Feature(name="longitude", type="double"),
    Feature(name="latitude", type="double"),
    Feature(name="meter_reading", type="double"),
    Feature(name="meter_increment", type="double"),
    Feature(name="passenger_count", type="int"),
]

fg = fs.create_feature_group(
    name="taxi_ride",
    version=1,
    primary_key=["ride_id"],
    statistics_config=False,
    online_enabled=True,
)

fg.save(features)
