#common.py

import streamlit as st
import pandas as pd
import os

# Constants for file paths
TESTS_CSV_FILE_PATH = 'Data/TestsList.csv'
WORDS_CSV_FILE_PATH = 'Data/WordsList.csv'
USERDATA_CSV_FILE_PATH = 'Data/UserData.csv'
CLASSDATA_CSV_FILE_PATH = 'Data/ClassData.csv'
ATTEMPTDATA_CSV_FILE_PATH = 'Data/AttemptData.csv'
PLACEHOLDER_IMAGE = 'Data/image/placeholder_image.png'

# File path for the CSV in the Streamlit environment
prd_TestsList_path = 'prd_Data/prd_TestsListData.csv'
prd_WordsList_path = 'prd_Data/prd_WordsListData.csv'
prd_UserData_path = 'prd_Data/prd_UserData.csv'
prd_ClassData_path = 'prd_Data/prd_ClassData.csv'
prd_AttemptData_path = 'prd_Data/prd_AttemptData.csv'
prd_Data_path = 'prd_Data/'
prd_Audio_path = 'prd_Data/prd_Audio'
prd_Temp_path = 'prd_Data/prd_Temp'

def initialize_folder(directory_path):
    # Create the directory if it doesn't exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        st.info(f"Successful create folder {directory_path}")
    else:
        st.info(f"Already exist folder {directory_path}")

def clear_files_in_folder(folder_path):
    """Remove all files in the specified folder."""
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        delete_file(file_path)

def delete_file(file_path):
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.remove(file_path)  # Remove the file
    except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def initialize_data():
    # Load CSV data
    df_test = read_csv_file(TESTS_CSV_FILE_PATH, prd_TestsList_path)
    df_word = read_csv_file(WORDS_CSV_FILE_PATH, prd_WordsList_path)
    df_user = read_csv_file(USERDATA_CSV_FILE_PATH, prd_UserData_path)
    df_class = read_csv_file(CLASSDATA_CSV_FILE_PATH, prd_ClassData_path)
    df_attempt = read_csv_file(ATTEMPTDATA_CSV_FILE_PATH, prd_AttemptData_path)
    # Clear variables to free up memory
    del df_test, df_word, df_user, df_class, df_attempt

def read_csv_file(repo_path, prd_path):
    """Read data from a CSV file."""
    try:
        if os.path.exists(prd_path):
            df = pd.read_csv(prd_path)
            #st.info("Data loaded from local storage.")
        else:
            # Initial load from a repository, as a fallback (if needed)
            df = pd.read_csv(repo_path)  # Replace with your default CSV
            df.to_csv(prd_path, index=False)  # Save to local environment
            #st.info("Data loaded from repository and saved to local storage.")
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        st.error(f"Error loading file: {repo_path} - {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return pd.DataFrame()

def save_to_csv(data, repo_path, prd_path):
    """Save data to the CSV file."""
    try:
        new_df = pd.DataFrame(data)
        if os.path.exists(prd_path):
            df = read_csv_file(repo_path, prd_path)
            df = pd.concat([df, new_df], ignore_index=True)
        else:
            df = new_df
        df.to_csv(prd_path, index=False)
        st.cache_data.clear()
        st.success("Data saved successfully.")
    except Exception as e:
        st.error(f"Error saving data to CSV: {e}")

def delete_from_csv(row_index, repo_path, prd_path):
    """Delete a row from the CSV file."""
    try:
        if os.path.exists(prd_path):
            df = read_csv_file(repo_path , prd_path)
            df = df.drop(index=row_index)
            df.to_csv(prd_path, index=False)
            st.cache_data.clear()
            st.success("Row deleted successfully.")
    except Exception as e:
        st.error(f"Error deleting row from CSV: {e}")

def update_to_csv(row_index, new_data, repo_path, prd_path):
    """Update a row in the CSV file."""
    try:
        if os.path.exists(prd_path):
            df = read_csv_file(repo_path, prd_path)
            df.loc[row_index] = new_data
            df.to_csv(prd_path, index=False)
            st.cache_data.clear()
            st.success("Data updated successfully.")
    except Exception as e:
        st.error(f"Error updating CSV file: {e}")  