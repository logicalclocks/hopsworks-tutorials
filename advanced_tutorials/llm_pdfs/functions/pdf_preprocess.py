from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import PyPDF2
import os
from typing import List, Dict, Union

def download_files_to_folder(folder_id: str, download_path: str) -> List:
    """
    Download files from a specified Google Drive folder to a local folder.

    Parameters:
    - folder_id (str): The ID of the Google Drive folder.
    - download_path (str): The local folder path where files will be downloaded.

    Returns:
    - List: A list containing information about newly downloaded files.
    """
    # Authenticate with Google Drive
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("credentials/credentials.json")

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()

    # Save the current credentials to a file
    gauth.SaveCredentialsFile("credentials/credentials.json")

    drive = GoogleDrive(gauth)

    # Create the local folder if it doesn't exist
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # List files in the specified Google Drive folder
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()

    # Initialize a list to store information about new files
    new_files = []
    print('⛳️ Loading...')

    # Iterate through each file in the list
    for file in file_list:
        # Check if the file already exists locally
        local_file_path = os.path.join(download_path, file["title"])

        if not os.path.isfile(local_file_path):
            # Download the file content and save it to the local folder
            file.GetContentFile(local_file_path)

            # Append information about the downloaded file to the list
            new_files.append(file)

    # Print the list of newly downloaded files
    if len(new_files) == 0:
        print("⛳️ There are no new files")
        return new_files
    
    print("⛳️ Newly downloaded files:")
    for file in new_files:
        print("title: %s, id: %s" % (file["title"], file["id"]))

    return new_files


def process_pdf_file(file_info: Dict, 
                     document_text: List,
                     pdfs_path: str = 'data/') -> List:
    """
    Process content of a PDF file and append information to the document_text list.

    Parameters:
    - file_info (Dict): Information about the PDF file.
    - document_text (List): List containing document information.
    - pdfs_path (str): Path to the folder containing PDF files (default is 'data/').

    Returns:
    - List: Updated document_text list.
    """
    file_title = file_info["title"]
    
    if file_title.split('.')[-1] == 'pdf':
        print(f'⛳️ File Name: {file_title}')
        
        pdf_path = os.path.join(pdfs_path, file_title)
        pdf_reader = PyPDF2.PdfReader(pdf_path)
        pages_amount = len(pdf_reader.pages)
        print(f'Amount of pages: {pages_amount}')
        
        for i, page in enumerate(pdf_reader.pages):
            document_text.append([file_title, file_info['embedLink'], i+1, page.extract_text()])
    return document_text
