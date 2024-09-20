import streamlit as st
import pandas as pd
import chardet
import os

# Define the expected column names
expected_columns = ['WordID', 'TestID', 'Word', 'LanguageCode', 'WordPhonetic', 'Description', 'Image']

# Define the required columns that must not have empty values
required_columns = ['TestID', 'Word', 'LanguageCode', 'Description']

def initial_check_csv_validity(df):
    # Check columns initially
    if list(df.columns) != expected_columns:
        st.warning(f'The CSV file must have the following columns: {expected_columns}', icon="⚠️")
        return False
    return True

def check_required_fields(df):
    #st.write("Checking required fields...")
    #st.write("Current columns in DataFrame:", df.columns.tolist())  # Debugging line
    # Check for missing values in required columns
    empty_value_warnings = []
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Column '{col}' is missing from the data.")
            return False
        if df[col].isnull().any() or df[col].eq("").any():
            missing_rows = df[df[col].isnull() | df[col].eq("")].index.tolist()
            empty_value_warnings.append(f"Column '{col}' has missing values in rows: {missing_rows}")
    if empty_value_warnings:
        for warning in empty_value_warnings:
            st.warning(warning, icon="⚠️")
        return False
    return True

def autogen_wordID(edited_df, csv_path):
    if os.path.exists(csv_path):
        existing_df = pd.read_csv(csv_path)
        if not existing_df['WordID'].empty:
            max_wordID = int(existing_df['WordID'].max())
        else:
            max_wordID = 0
    else:
        max_wordID = 0

    new_wordIDs = range(max_wordID + 1, max_wordID + 1 + len(edited_df))
    edited_df['WordID'] = new_wordIDs

    return edited_df

def save_to_csv(dataframe, path):
    if os.path.exists(path):
        existing_df = pd.read_csv(path)
        updated_df = pd.concat([existing_df, dataframe], ignore_index=True)
    else:
        updated_df = dataframe
    updated_df.to_csv(path, index=False, encoding='utf-8-sig')

def show_upload_page():
    st.write("### Upload Words from CSV")
    
    # Step 1: File uploader widget
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
    if uploaded_file is not None:
        # Step 2: Check encoding
        raw_data = uploaded_file.read()
        result = chardet.detect(raw_data)
        uploaded_file.seek(0)  # Reset file pointer to the start

        encoding = result['encoding']
        if encoding != 'UTF-8-SIG':
            st.warning('The file must be in CSV UTF-8 with BOM encoding.')
        else:
            # Step 3: Load the CSV data
            df = pd.read_csv(uploaded_file)

            # Step 4: Validate the CSV file initially (only columns)
            if initial_check_csv_validity(df):
                # After initial validation, validate the data content
                if check_required_fields(df):
                    st.success("The file is valid. You can edit the data below if needed.")
                    st.session_state['valid'] = True
                else:
                    st.warning("Please correct the issues below and re-submit.")
                    st.session_state['valid'] = False
            
            # Step 5: Display and edit the data using st.data_editor
            edited_df = st.data_editor(df, key="data_editor")

            # Step 6: Handle the "Re-validate" button click
            if st.button("Re-validate"):
                                
                # Extract the actual data from the session state
                data_editor_state = st.session_state['data_editor']
                
                if isinstance(data_editor_state, pd.DataFrame):
                    edited_df = data_editor_state
                elif isinstance(data_editor_state, dict):
                    if 'edited_rows' in data_editor_state and data_editor_state['edited_rows']:
                        edited_df.update(pd.DataFrame(data_editor_state['edited_rows']))
                    if 'added_rows' in data_editor_state and data_editor_state['added_rows']:
                        new_rows_df = pd.DataFrame(data_editor_state['added_rows'])
                        edited_df = pd.concat([edited_df, new_rows_df], ignore_index=True)
                    if 'deleted_rows' in data_editor_state and data_editor_state['deleted_rows']:
                        edited_df.drop(index=data_editor_state['deleted_rows'], inplace=True)

                # Re-validate only the required fields
                if check_required_fields(edited_df):
                    st.success("The edited file is now valid. You can complete the process.")
                    st.session_state['valid'] = True
                else:
                    st.error("There are still issues with the data. Please correct them and re-submit.")
                    st.session_state['valid'] = False

            # Step 7: Complete button to save validated data
            if st.button("Complete", disabled=not st.session_state.get('valid', False)):
                # Call autogen_wordID to update WordID in the edited_df
                edited_df = autogen_wordID(edited_df, 'prd_Data/prd_WordsListData.csv')
                
                # Save the updated DataFrame to the CSV file
                save_to_csv(edited_df, 'prd_Data/prd_WordsListData.csv')
                st.success("The data has been successfully added to the existing CSV file.")

    if st.button("🔙 Back"):
        st.session_state.page = 'table'
        st.rerun()

# To trigger the upload page display
# show_upload_page()
