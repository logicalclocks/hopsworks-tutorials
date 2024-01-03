import hopsworks
import os
import time
from mage_ai.data_preparation.shared.secrets import get_secret_value
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def deploy_model(data, *args, **kwargs):
    """
    Deploys the trained XGBoost classifier.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)
    """
    # Specify your data exporting logic here
    project = hopsworks.login(
        api_key_value=get_secret_value('HOPSWORKS_API_KEY'),
        )

    fs = project.get_feature_store()
    # Get the model registry
    mr = project.get_model_registry()

    # Get model object
    fraud_model = mr.get_model(
        name="fraud", 
        version=1,
    )
    print('Model is here!')
  
    # Get the dataset API from the project
    dataset_api = project.get_dataset_api()

    # Specify the file to upload ("predict_example.py") to the "Models" directory, and allow overwriting
    uploaded_file_path = dataset_api.upload(
        "predictor_script.py", 
        "Models", 
        overwrite=True,
        )

    # Construct the full path to the uploaded predictor script
    predictor_script_path = os.path.join(
        "/Projects", 
        project.name, 
        uploaded_file_path,
        )

    # Deploy the fraud model
    deployment = fraud_model.deploy(
        name="fraud",                       # Specify the deployment name
        script_file=predictor_script_path,  # Provide the path to the predictor script
    )

    print("Deployment is warming up...")
    time.sleep(45)
