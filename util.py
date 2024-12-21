import os
import pandas as pd

# Function to save data in batches
def save_to_csv(data, file_name):
    df = pd.DataFrame(data)
    if os.path.exists(file_name):
        df.to_csv(file_name, mode='a', header=False, index=False, encoding='utf-8-sig')  # Append mode
    else:
        df.to_csv(file_name, index=False, encoding='utf-8-sig')

# Function to save the current page number to track progress
def save_progress(page_number, file_name):
    with open(file_name, 'w') as f:
        f.write(str(page_number))

# Function to load the last scraped page number from file
def load_progress(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            return int(f.read().strip())
    return 1  # Start from page 1 if no progress file exists
