import pandas as pd
import datetime
import numpy as np

# On-Demand feature function
def zipcode(address):
    zip_code=int(address)
    l=len(str(zip_code))
    if l==5:
        return str(zip_code)
    return "0"
