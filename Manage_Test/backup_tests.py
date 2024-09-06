import streamlit as st
import pandas as pd
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.title('Back up data')
st.write('This is a page to download all data from host')

# Set the directory where your CSV files are stored
folder_path = "prd_Data"  # Change this to your CSV directory path

# Loop through each file in the directory
if os.path.exists(folder_path):  # Check if the folder exists and is a directory
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)

            # Read the file contents
            with open(file_path, "rb") as file:
                file_bytes = file.read()

            # Create a download button for each file
            st.download_button(
                label=f"Download {filename}",
                data=file_bytes,
                file_name=filename,
                mime="text/csv"
            )
else: 
    st.warning(f"Cannot find '{folder_path}' folder")