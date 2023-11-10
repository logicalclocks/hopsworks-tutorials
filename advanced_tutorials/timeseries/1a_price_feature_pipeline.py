import hopsworks
from features.price import generate_today
import warnings
warnings.filterwarnings('ignore')

# Generate price data form today
generated_data_today = generate_today()

# Connect to the Feature Store
project = hopsworks.login()
fs = project.get_feature_store() 

# Retrieve Price Feature Group
price_fg = fs.get_feature_group(
    name='price',
    version=1,
)
# Insert generated data for today into Price Feature Group
price_fg.insert(generated_data_today)
