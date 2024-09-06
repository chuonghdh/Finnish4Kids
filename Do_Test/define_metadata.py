import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import logging
import time
import os
#from Do_Test.do_test import main_do_test

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for file paths
TESTS_CSV_FILE_PATH = 'Data/TestsList.csv'
USERDATA_CSV_FILE_PATH = 'Data/UserData.csv'
CLASSDATA_CSV_FILE_PATH = 'Data/ClassData.csv'
ATTEMPTDATA_CSV_FILE_PATH = 'Data/AttemptData.csv'
PLACEHOLDER_IMAGE = "Data/image/placeholder_image.png"
IMAGE_SIZE = 140  # Set this to the desired thumbnail size

# File path for the CSV in the Streamlit environment
prd_UserData_path = 'prd_Data/prd_UserData.csv'
prd_ClassData_path = 'prd_Data/prd_ClassData.csv'
prd_AttemptData_path = 'prd_Data/prd_AttemptData.csv'
prd_TestsList_path = 'prd_Data/prd_TestsListData.csv'

def read_csv_file(repo_path, prd_path):
    """Read data from a CSV file."""
    try:
        #df = pd.read_csv(filename)
        #logger.info(f"Successfully loaded data from {filename}")
        
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
        logger.error(f"Error loading file: {repo_path} - {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        logger.exception(f"Unexpected error occurred while reading the CSV file.")
        return pd.DataFrame()

def get_new_id(df, column_name):
    """Generate a new ID for a given DataFrame column."""
    return 1 if df.empty else df[column_name].max() + 1

def save_to_csv(df, filepath, success_message):
    """Save a DataFrame to a CSV file and display a success message."""
    df.to_csv(filepath, index=False)
    st.success(success_message)

def main_define_metadata():
    """Show the editor for a specific TestID."""
    if st.session_state.page == 'prep_test':
        selected_test = st.session_state.get("selected_test")
        if not selected_test:
            st.write("No TestID selected.")
            return
    else: 
        st.session_state.page == 'test_list'
        return

    test_id = int(selected_test)

    st.title("Pre-Test")

    # Load CSV data
    df_test = read_csv_file(TESTS_CSV_FILE_PATH, prd_TestsList_path)
    df_user = read_csv_file(USERDATA_CSV_FILE_PATH, prd_UserData_path)
    df_class = read_csv_file(CLASSDATA_CSV_FILE_PATH, prd_ClassData_path)
    df_attempt = read_csv_file(ATTEMPTDATA_CSV_FILE_PATH, prd_AttemptData_path)

    # Filter for the selected TestID
    test_info = df_test[df_test['TestID'] == test_id]
    if test_info.empty:
        st.write(f"No data found for TestID {test_id} in TestsList.csv")
        return

    # Display test details
    st.write(f"### {test_id} - {test_info['TestName'].values[0]} (Language: {test_info['TestLanguage'].values[0]})")
    
    # User and Class selection
    cols = st.columns([1, 1])
    with cols[0]:
        selected_user_name = st.selectbox("Select User", options=df_user['UserName'])
        with st.expander("Create new User Name:"):
            new_user_input = st.text_input("Enter your User Name 👇", max_chars=20, label_visibility='collapsed').strip()
            if st.button("Add User Name"):
                if not new_user_input:
                    st.warning("Please input User Name!")
                elif new_user_input.lower() in df_user["UserName"].str.lower().values:
                    st.warning("The User Name already exists!")
                else:
                    new_user_df = pd.DataFrame({
                        'UserID': [get_new_id(df_user, 'UserID')],
                        'UserName': new_user_input,
                        'Password': ['123456']  # Default password for new users
                    })
                    df_user = pd.concat([df_user, new_user_df], ignore_index=True)
                    save_to_csv(df_user, prd_UserData_path, "New User Name recorded successfully.")
                    time.sleep(0.8)
                    st.rerun()

    with cols[1]:
        selected_class_name = st.selectbox("Select Class", df_class['ClassName'])
        with st.expander("Create new Class Name:"):
            sub_cols = st.columns([1, 1])
            with sub_cols[0]:
                new_class_input = st.text_input("Enter your Class Name 👇", max_chars=20, label_visibility='collapsed').strip()
            with sub_cols[1]:
                new_teacher_input = st.text_input("Enter your Teacher Name 👇", max_chars=20, label_visibility='collapsed').strip()
            if st.button("Add New Class"):
                if not new_class_input:
                    st.warning("Please input Class Name!")
                elif new_class_input.lower() in df_class["ClassName"].str.lower().values:
                    st.warning("The Class Name already exists!")
                else:
                    new_class_df = pd.DataFrame({
                        'ClassID': [get_new_id(df_class, 'ClassID')],
                        'ClassName': new_class_input,
                        'TeacherName': new_teacher_input  #Temp can leave blank
                    })
                    df_class = pd.concat([df_class, new_class_df], ignore_index=True)
                    save_to_csv(df_class, prd_ClassData_path, "New Class Name recorded successfully.")
                    time.sleep(0.8)
                    st.rerun()
    # Action buttons
    button_cols = st.columns([1, 2, 1])
    with button_cols[0]:
        if st.button("🔙 Back", key='prep_test_back'):
            st.session_state.page = 'test_list'
            st.session_state.selected_test = None
            st.rerun()
    with button_cols[1]:
        st.write(" ")
    with button_cols[2]:
        if st.button("Do Test", key='prep_test_do_test'):
            selected_user_id = df_user.loc[df_user['UserName'] == selected_user_name, 'UserID'].values[0]
            selected_class_id = df_class.loc[df_class['ClassName'] == selected_class_name, 'ClassID'].values[0]
            new_attempt_id = get_new_id(df_attempt, 'AttemptID')
        
            new_attempt_df = pd.DataFrame({
                'AttemptID': [new_attempt_id],
                'UserID': [selected_user_id],
                'ClassID': [selected_class_id],
                'TestID': [test_id],
                'TotalQuestion': [''],
                'CorrectList': [''],
                'WrongList': ['']
            })

            df_attempt = pd.concat([df_attempt, new_attempt_df], ignore_index=True)
            save_to_csv(df_attempt, prd_AttemptData_path, "Test attempt recorded successfully.")
            st.session_state.page = 'do_test'
            st.session_state.word_index = 1
            st.session_state.show_image = True
            time.sleep(0.5)
            st.rerun()
            

# Run the main function
main_define_metadata()
