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
    label_map = {'Madrid': 0, 'Sevilla': 1, 'Napoli': 2}
    return label_map.get(city_name, -1)  # Return -1 if city_name is not found in label_map


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
    mean = 14.5  # Mean value of the sample 'pm2_5' column
    std = 13  # Standard deviation

    scaled_pm2_5 = (pm2_5_value - mean) / std
    return scaled_pm2_5