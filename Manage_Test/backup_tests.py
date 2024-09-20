import streamlit as st
import pandas as pd
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_dir():
    # Get the current working directory
    current_dir = os.getcwd()

    # List all items in the current directory
    items_in_dir = os.listdir(current_dir)

    # Filter out only directories
    directories = [item for item in items_in_dir if os.path.isdir(os.path.join(current_dir, item))]

    # Print the directories using Streamlit
    st.write(f"Directories in {current_dir}:")
    for directory in directories:
        st.write(directory)

st.title('Back up data')
st.write('This is a page to download all data from host')

# Set the directory where your CSV files are stored
folder_path = "prd_Data"  # Change this to your CSV directory path

# Loop through each file in the directory
if os.path.exists(folder_path):  # Check if the folder exists and is a directory
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)

            # Read the file contents with UTF-8 BOM encoding
            with open(file_path, "r", encoding="utf-8-sig") as file:
                file_content = file.read()

            # Convert the content back to bytes for the download button
            file_bytes = file_content.encode("utf-8-sig")

            # Create a download button for each file
            st.download_button(
                label=f"Download {filename}",
                data=file_bytes,
                file_name=filename,
                mime="text/csv"
            )
else: 
    st.warning(f"Cannot find '{folder_path}' folder")