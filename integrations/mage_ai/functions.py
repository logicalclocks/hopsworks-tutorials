import numpy as np

# Define a function to compute Haversine distance between consecutive coordinates
def haversine(long, lat):
    """Compute Haversine distance between each consecutive coordinate in (long, lat)."""

    # Shift the longitude and latitude columns to get consecutive values
    long_shifted = long.shift()
    lat_shifted = lat.shift()

    # Calculate the differences in longitude and latitude
    long_diff = long_shifted - long
    lat_diff = lat_shifted - lat

    # Haversine formula to compute distance
    a = np.sin(lat_diff/2.0)**2
    b = np.cos(lat) * np.cos(lat_shifted) * np.sin(long_diff/2.0)**2
    c = 2*np.arcsin(np.sqrt(a + b))

    return c