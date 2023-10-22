import hopsworks

from hsfs.feature import Feature

project = hopsworks.login()
fs = project.get_feature_store()

features = [
    Feature(name="cc_num", type="bigint"),
    Feature(name="num_trans_per_10m", type="bigint"),
    Feature(name="avg_amt_per_10m", type="double"),
    Feature(name="stdev_amt_per_10m", type="double"),
]

fg = fs.create_feature_group(
    "card_transactions_10m_agg",
    version=1,
    statistics_config=False,
    primary_key=["cc_num"],
    online_enabled=True,
    stream=True,
)

fg.save(features)
