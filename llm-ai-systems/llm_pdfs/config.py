import torch

# The unique identifier for the Google Drive folder where your PDF files are stored
FOLDER_ID = '{YOUR_FOLDER_ID}'

# The local directory path where downloaded data will be saved.
DOWNLOAD_PATH = "data"

# The identifier of the pre-trained sentence transformer model for producing sentence embeddings.
MODEL_SENTENCE_TRANSFORMER = 'all-MiniLM-L6-v2'

# The computing device to be used for model inference and training.
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# The identifier for the Mistral-7B-Instruct model
MODEL_ID = 'mistralai/Mistral-7B-Instruct-v0.2'
