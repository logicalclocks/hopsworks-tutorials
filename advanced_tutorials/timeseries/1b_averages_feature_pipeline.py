from datetime import datetime, timedelta
from features.averages import calculate_second_order_features
import hopsworks
import warnings
warnings.filterwarnings('ignore')

# Connect to the Feature Store
project = hopsworks.login()
fs = project.get_feature_store()

# Retrieve Feature Groups
averages_fg = fs.get_feature_group(
    name='averages', 
    version=1,
)
price_fg = fs.get_feature_group(
    name='prices', 
    version=1,
)

# Get today's date and 30 days ago as timestamps
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
thirty_days_ago = today - timedelta(days=31)

# Read price data using timestamp
month_price_data = price_fg.filter(price_fg.date >= thirty_days_ago).read()

# Calculate second order features
averages_df = calculate_second_order_features(month_price_data)

# Convert today's date to string format for filtering
today_str = today.strftime("%Y-%m-%d")

# Filter for today's data
averages_today = averages_df[averages_df['date'].dt.strftime("%Y-%m-%d") == today_str]

# Insert second order features for today
averages_fg.insert(averages_today)
