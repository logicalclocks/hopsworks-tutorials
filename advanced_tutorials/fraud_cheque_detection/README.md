# 🏦 Cheque Fraud Detection

## 👨🏻‍🏫 Overview

The Cheque Fraud Detection project is designed to identify fraudulent cheques and provide detailed explanations for each validation. The project encompasses three main components: feature pipeline, training pipeline, and inference pipeline. 

## 📖 Feature Pipeline

The Feature Pipeline does the following:

1. **Data Loading**: The process begins with downloading the dataset into a pandas DataFrame. Initial data exploration is conducted to understand the structure and distribution of the data.

2. **Feature Engineering**: Key features are extracted from the raw data, including textual corrections and matching the amount written in words with the numerical amount. These features are essential for training an effective fraud detection model.

4. **Feature Group Creation**: Create a **Cheque Feature Group** to store your cheque data.

This notebook lays the groundwork for building a robust fraud detection model by ensuring the data is accurate, consistent, and ready for the training phase.

## 🏃🏻‍♂️ Training Pipeline

The Training Pipeline notebook focuses on building and evaluating the fraud detection model. This phase is crucial for developing a robust classifier capable of accurately identifying fraudulent cheques. The notebook includes several important steps:

1. **Data Import and Setup**: The notebook begins by importing the necessary libraries and connecting to the Hopsworks feature store. This setup phase ensures that all required resources and datasets are accessible.

2. **Feature Retrieval**: Create a **Feature View** with selected features and retrieve a train-test split for model training.

3. **Model Training**: An XGBoost classifier is trained using the retrieved features. XGBoost is chosen for its efficiency and high performance in classification tasks. The model learns to differentiate between valid and fraudulent cheques based on the provided features.

4. **Model Evaluation**: The trained model is evaluated using various metrics, including accuracy, precision, recall, F1 score, and confusion matrix. These metrics provide a comprehensive understanding of the model's performance and highlight areas for potential improvement.

5. **Model Saving**: The trained model is saved in the **Hopsworks Model Registry**.

## 🚀 Inference Pipeline

The Inference Pipeline notebook is designed to make predictions on new cheques and provide detailed explanations for each validation. This phase is crucial for deploying the model in a real-world scenario, where it can validate cheques and explain the reasons behind its decisions. The notebook includes the next steps:

1. **Model Loading**: The trained XGBoost model is loaded from the **Hopsworks Model Registry** to perform inference on new data. Additionally, the `Donut OCR model` is loaded for text extraction from cheque images.

2. **Text Parsing and Validation**: `Donut OCR` is used to parse text from new cheque images. This step extracts the necessary textual data, such as the written amount, for validation against numerical data.

3. **Fraud Detection**: The extracted features are fed into the trained model to predict whether a cheque is fraudulent or valid. This prediction is based on the learned patterns from the training phase.

4. **LLM Loading**: Load the `meta-llama/Meta-Llama-3-8B-Instruct` model and set up LLM Chain for text generation using Langchain.

5. **Explanation Generation**: An LLM chain is used to generate detailed explanations for each validation result. This step leverages a Large Language Model to provide insights into why a cheque is considered fraudulent or valid, enhancing transparency and understanding.

6. **Batch Inference**: The notebook also supports batch inference, allowing multiple cheques to be processed at once. Then validations and correcponding descriptions are saved in the **cheque_validation** Feature Group. This is useful for validating large volumes of cheques efficiently. 

## 🛠 Setup and Installation

1. Clone the Repository:

```
git clone https://github.com/logicalclocks/hopsworks-tutorials.git
cd hopsworks-tutorials/advanced_tutorials/fraud_cheque_detection
```

2. Install Dependencies:

```
pip install -r requirements.txt
```

3. Run Notebooks Sequentially:

- Start with `1_feature_pipeline.ipynb` to preprocess and store features.
- Proceed with `2_training_pipeline.ipynb` to train and save the model.
- Finally, execute `3_inference_pipeline.ipynb` to perform predictions and generate explanations.

---

