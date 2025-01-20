import hopsworks
from hsfs.feature import Feature

# 1) Connect to your Hopsworks project
project = hopsworks.login()
fs = project.get_feature_store()

# 2) Define the metadata for each feature in your POJO
features = [
    Feature(name="id", type="int"),
    Feature(name="timestamp", type="timestamp"),
    Feature(name="boolean_flag", type="boolean"),
    Feature(name="byte_value", type="int"),
    Feature(name="short_int", type="int"),
    Feature(name="low_cat_int", type="int"),
    Feature(name="high_cat_int", type="int"),
    Feature(name="long_col", type="bigint"),
    Feature(name="float_zero_std", type="float"),
    Feature(name="float_low_std", type="float"),
    Feature(name="float_high_std", type="float"),
    Feature(name="double_value", type="double"),
    Feature(name="decimalValue", type="double"),
    Feature(name="timestamp_col", type="timestamp"),
    Feature(name="date_col", type="date"),
    Feature(name="string_low_cat", type="string"),
    Feature(name="string_high_cat", type="string"),
    Feature(name="array_column", type="array<int>"),
]

# 3) Create a new Feature Group (adjust the name/version as desired)
fg = fs.create_feature_group(
    name="java_data",
    version=1,
    description="Feature Group for the Java POJO DataRow example",
    primary_key=["id"],
    event_time="timestamp",
    online_enabled=True,
    stream=True,
    statistics_config=False
)

# 4) Save feature metadata to Hopsworks
if fg.id is None:
    fg.save(features)
