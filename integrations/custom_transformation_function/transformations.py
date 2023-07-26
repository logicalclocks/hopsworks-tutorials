def encode_city_name(city_name):
    """
    Encode the 'city_name' element using a custom LabelEncoder-like approach.

    Parameters:
        city_name (str):
            The 'city_name' element to be encoded.

    Returns:
        int:
            The encoded city name as an integer.
    """
    # Define a mapping of city names to their corresponding integer labels
    label_map = {
        'Amsterdam': 0, 'Athina': 1, 'Berlin': 2, 'Gdansk': 3, 'Kraków': 4,
        'London': 5, 'Madrid': 6, 'Marseille': 7, 'Milano': 8, 'München': 9,
        'Napoli': 10, 'Paris': 11, 'Sevilla': 12, 'Stockholm': 13, 'Tallinn': 14,
        'Varna': 15, 'Wien': 16
    }
    
    # Return the integer label for the input city_name using label_map.get()
    # If the city_name is not found in label_map, return -1 as the default value
    return label_map.get(city_name, -1)


def scale_pm2_5(pm2_5_value):
    """
    Scale the 'pm2_5' value using custom scaling.

    Parameters:
        pm2_5_value (float):
            The 'pm2_5' value to be scaled.

    Returns:
        float:
            The scaled 'pm2_5' value.
    """
    # Define the mean value of the 'pm2_5' column for the scaling process
    mean = 14.5

    # Define the standard deviation value of the 'pm2_5' column for the scaling process
    std = 13

    # Calculate the scaled 'pm2_5' value using the custom scaling formula
    scaled_pm2_5 = (pm2_5_value - mean) / std

    # Return the scaled 'pm2_5' value
    return scaled_pm2_5
