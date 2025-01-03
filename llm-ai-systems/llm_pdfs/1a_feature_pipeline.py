import PyPDF2
import pandas as pd
from sentence_transformers import SentenceTransformer

from functions.pdf_preprocess import download_files_to_folder, process_pdf_file
from functions.text_preprocess import process_text_data
import config

import hopsworks

def pipeline():
    # Call the function to download files
    new_files = download_files_to_folder(
        config.FOLDER_ID, 
        config.DOWNLOAD_PATH,
    )
    
    if len(new_files) == 0:
        print('⛳️ Your folder is up to date!')
        return
    
    # Initialize an empty list
    document_text = []

    for file in new_files:
        process_pdf_file(
            file, 
            document_text, 
            config.DOWNLOAD_PATH,
        )
        
    # Create a DataFrame
    columns = ["file_name", "page_number", "text"]
    df_text = pd.DataFrame(
        data=document_text,
        columns=columns,
    )

    # Process text data using the process_text_data function
    df_text_processed = process_text_data(df_text)

    # Retrieve a SentenceTransformer
    model = SentenceTransformer(
        config.MODEL_SENTENCE_TRANSFORMER,
    ).to(config.DEVICE)

    # Generate embeddings for the 'text' column using the SentenceTransformer model
    df_text_processed['embeddings'] = pd.Series(
        model.encode(df_text_processed['text']).tolist(),
    )

    # Create a new column 'context_id' with values ranging from 0 to the number of rows in the DataFrame
    df_text_processed['context_id'] = [*range(df_text_processed.shape[0])]


    project = hopsworks.login()

    fs = project.get_feature_store() 

    documents_fg = fs.get_feature_group(
        name="documents_fg",
        version=1,
    )

    documents_fg.insert(df_text_processed)
    return

if __name__ == '__main__':
    pipeline()
