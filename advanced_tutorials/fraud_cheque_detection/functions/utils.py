import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

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
