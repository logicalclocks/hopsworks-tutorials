import hopsworks

from hsfs.feature import Feature

project = hopsworks.login()
fs = project.get_feature_store()

# Setup the feature groups for the bytewax pipelines
# Price Features
features = [
    Feature(name="ticker", type="string"),
    Feature(name="timestamp", type="timestamp"),
    Feature(name="bid", type="float"),
    Feature(name="ask", type="float"),
    Feature(name="ask_price", type="float"),
    Feature(name="spread", type="float"),
]

fg = fs.create_feature_group(
    name="order_book",
    version=1,
    primary_key=["ticker"],
    event_time="timestamp",
    statistics_config=False,
    online_enabled=True,
)

fg.save(features)
