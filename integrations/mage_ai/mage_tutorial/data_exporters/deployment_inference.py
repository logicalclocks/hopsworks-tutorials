import hopsworks
from mage_ai.data_preparation.shared.secrets import get_secret_value
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def inference(data, *args, **kwargs):
    """
    Deployment inference.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)
    """
    # Specify your data exporting logic here
    project = hopsworks.login(
        api_key_value=get_secret_value('HOPSWORKS_API_KEY'),
    )

    # get Hopsworks Model Serving
    ms = project.get_model_serving()

    # get deployment object
    deployment = ms.get_deployment("fraud")

    # Start the deployment and wait for it to be running, with a maximum waiting time of 480 seconds
    deployment.start(await_running=480)

    # Make predictions using the deployed model
    predictions = deployment.predict(
        inputs=[4700702588013561],
    )
    print(f'⛳️ Prediction: {predictions}')

    deployment.stop()

    print('🔮 Deployment is stopped!')
