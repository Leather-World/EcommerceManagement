import os
import pandas as pd

# Set directory containing CSV files
csv_dir = r"Amazon/"

# Get list of all CSV files in directory
csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

# Create empty DataFrame to store concatenated data
concat_df = pd.DataFrame()

# Loop through each CSV file, read it into a DataFrame, and concatenate it to concat_df
for file in csv_files:
    filepath = os.path.join(csv_dir, file)
    df = pd.read_csv(filepath)
    concat_df = pd.concat([concat_df, df])

# Write concatenated DataFrame to a new CSV file
concat_df.to_csv("Amazon_RR_Jan1toAPril30_data.csv", index=False)
