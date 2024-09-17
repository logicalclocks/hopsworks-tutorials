import hopsworks
import xgboost as xgb
import pandas as pd
import os
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from matplotlib import pyplot
import seaborn as sns
import joblib
from hsml.schema import Schema
from hsml.model_schema import ModelSchema
from mage_ai.data_preparation.shared.secrets import get_secret_value
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


def prepare_training_data(X_train, X_test, y_train, y_test):
    # Sort the training features DataFrame 'X_train' based on the 'datetime' column
    X_train = X_train.sort_values("datetime")

    # Reindex the target variable 'y_train' to match the sorted order of 'X_train' index
    y_train = y_train.reindex(X_train.index)

    # Sort the test features DataFrame 'X_test' based on the 'datetime' column
    X_test = X_test.sort_values("datetime")

    # Reindex the target variable 'y_test' to match the sorted order of 'X_test' index
    y_test = y_test.reindex(X_test.index)

    # Drop the 'datetime' column from the training features DataFrame 'X_train'
    X_train.drop(["datetime"], axis=1, inplace=True)

    # Drop the 'datetime' column from the test features DataFrame 'X_test'
    X_test.drop(["datetime"], axis=1, inplace=True)

    return X_train, X_test, y_train, y_test


@data_exporter
def train_model(data, *args, **kwargs):
    """
    Train an XGBoost classifier for fraud detection and save it in the Hopsworks Model Registry.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)
    """
    TEST_SIZE = 0.2

    # Specify your data exporting logic here
    project = hopsworks.login(
        api_key_value=get_secret_value('HOPSWORKS_API_KEY'),
        )

    fs = project.get_feature_store()

    # Get the 'transactions_view' feature view
    feature_view = fs.get_feature_view(
        name='transactions_view',
        version=1,
    )

    X_train, X_test, y_train, y_test = feature_view.train_test_split(
        description='transactions fraud training dataset',
        test_size=TEST_SIZE,
    )

    X_train, X_test, y_train, y_test = prepare_training_data(
        X_train, 
        X_test, 
        y_train, 
        y_test,
    )
    X_train.to_csv(f'X_train.csv')

    # Create an XGBoost classifier
    model = xgb.XGBClassifier()

    # Fit XGBoost classifier to the training data
    model.fit(X_train, y_train)

    # Predict the training data using the trained classifier
    y_pred_train = model.predict(X_train)

    # Predict the test data using the trained classifier
    y_pred_test = model.predict(X_test)

    # Compute f1 score
    metrics = {
        "f1_score": f1_score(y_test, y_pred_test, average='macro')
    }

    # Calculate and print the confusion matrix for the test predictions
    results = confusion_matrix(y_test, y_pred_test)
    print(results)

    # Create a DataFrame for the confusion matrix results
    df_cm = pd.DataFrame(
        results, 
        ['True Normal', 'True Fraud'],
        ['Pred Normal', 'Pred Fraud'],
    )

    # Create a heatmap using seaborn with annotations
    cm = sns.heatmap(df_cm, annot=True)

    # Get the figure and display it
    fig = cm.get_figure()

    # Create a Schema for the input features using the values of X_train
    input_schema = Schema(X_train.values)

    # Create a Schema for the output using y_train
    output_schema = Schema(y_train)

    # Create a ModelSchema using the defined input and output schemas
    model_schema = ModelSchema(
        input_schema=input_schema, 
        output_schema=output_schema,
        )

    # Convert the model schema to a dictionary for inspection
    model_schema.to_dict()

    # Specify the directory name for saving the model and related artifacts
    model_dir = "quickstart_fraud_model"

    # Check if the directory already exists; if not, create it
    if not os.path.isdir(model_dir):
        os.mkdir(model_dir)

    # Save the trained XGBoost classifier to a joblib file in the specified directory
    joblib.dump(model, model_dir + '/xgboost_model.pkl')

    # Save the confusion matrix heatmap figure to an image file in the specified directory
    fig.savefig(model_dir + "/confusion_matrix.png")

    # Get the model registry
    mr = project.get_model_registry()

    # Create a Python model named "fraud" in the model registry
    fraud_model = mr.python.create_model(
        name="fraud", 
        metrics=metrics,             # Specify the metrics used to evaluate the model
        model_schema=model_schema,   # Use the previously defined model schema
        input_example=[4700702588013561],  # Provide an input example for testing deployments
        description="Quickstart Fraud Predictor",  # Add a description for the model
    )

    # Save the model to the specified directory
    fraud_model.save(model_dir)