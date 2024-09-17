import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import requests
import zipfile
import os


def load_image(image_name, folder_name='data/images/'):
    """
    Loads an image from a specified folder and converts it to RGB format.

    Parameters:
    - image_name (str): The name of the image file to load.
    - folder_name (str, optional): The directory path where image files are stored. Defaults to 'data/images/'.

    Returns:
    - Image: An Image object in RGB format.
    """
    # Open the image file and convert it to RGB to ensure consistent color format
    image = Image.open(folder_name + image_name).convert('RGB')
    return image


def show_image(image):
    """
    Displays an image using matplotlib with specific figure sizing and no axis.

    Parameters:
    - image: An Image object or an array-like object that can be visualized through matplotlib.

    Effects:
    - This function displays the image on a 10x6 inch figure without axes.
    """
    # Create a figure object with specified dimensions
    fig = plt.figure(figsize=(10, 6))
    # Convert the image object to a numpy array for displaying
    image_array = np.array(image)
    # Display the image array
    plt.imshow(image_array)
    # Hide the axes of the plot
    plt.axis('off')
    # Show the plot
    plt.show()
        

def download_and_extract_zip(url: str, extract_to: str = '.') -> None:
    """
    Download a .zip file from a given URL and extract it into the specified directory.
    
    This function handles the downloading and extraction of a zip file from a specified URL.
    It saves the zip file to the local directory, extracts it to a target directory, and handles
    basic HTTP status checks to ensure the file is downloaded correctly.

    Args:
    url (str): The URL of the .zip file to download.
    extract_to (str): Directory to extract the files into, defaults to the current directory.
    
    Raises:
    Exception: Raises an exception if the file could not be downloaded (non-200 status code).
    """
    # Get the filename from the URL by splitting it and getting the last segment
    filename = url.split('/')[-1]

    # Attempt to download the file with HTTP GET request
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        # Write the response content to a file in binary write mode
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename}")

        # Extract the .zip file using the ZipFile class
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Extracted {filename} to {extract_to}")
    else:
        # If the download fails, raise an exception with the status code
        raise Exception(f"❌ Failed to download the file. Status code: {response.status_code}")
