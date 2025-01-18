import hopsworks
from hsfs.feature import Feature

# 1) Connect to your Hopsworks project
project = hopsworks.login()
fs = project.get_feature_store()

# 2) Define the metadata for each feature in your POJO
features = [
    Feature(name="id", type="int"),
    Feature(name="timestamp", type="datetime"),
    Feature(name="booleanFlag", type="boolean"),
    Feature(name="byteValue", type="int"),
    Feature(name="shortInt", type="int"),
    Feature(name="lowCatInt", type="int"),
    Feature(name="highCatInt", type="int"),
    Feature(name="longCol", type="bigint"),
    Feature(name="floatZeroStd", type="float"),
    Feature(name="floatLowStd", type="float"),
    Feature(name="floatHighStd", type="float"),
    Feature(name="doubleValue", type="double"),
    Feature(name="decimalValue", type="double"),
    Feature(name="timestampCol", type="datetime"),
    Feature(name="dateCol", type="date"),
    Feature(name="stringLowCat", type="string"),
    Feature(name="stringHighCat", type="string"),
    Feature(name="arrayColumn", type="array<int>"),
]

# 3) Create a new Feature Group (adjust the name/version as desired)
fg = fs.create_feature_group(
    name="java_data_row",
    version=1,
    description="Feature Group for the Java POJO DataRow example",
    primary_key=["id"],
    event_time="timestamp",
    online_enabled=True,
    statistics_config=False
)

# 4) Save feature metadata to Hopsworks
fg.save(features)
