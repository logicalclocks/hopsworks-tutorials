import pandas as pd

def prepare_customers(df):
    df['club_member_status'].fillna('ABSENT', inplace=True)
    df.dropna(subset=['age'], inplace=True)
    
    age_bins = [0, 18, 25, 35, 45, 55, 65, 100]
    age_labels = ['0-18', '19-25', '26-35', '36-45', '46-55', '56-65', '66+']
    df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels)
        
    df.dropna(axis=1, inplace=True)
    return df
