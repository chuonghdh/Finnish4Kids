import streamlit as st
import pandas as pd
import common as cm
import os
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Constants
# TESTS_CSV_FILE_PATH = 'Data/TestsList.csv'  # Adjust the path if necessary
# WORDS_CSV_FILE_PATH = 'Data/WordsList.csv'  # Adjust the path if necessary

# File path for the CSV in the Streamlit environment
# prd_TestsList_path = 'prd_Data/prd_TestsListData.csv'
# prd_WordsList_path = 'prd_Data/prd_WordsListData.csv'

# def read_csv_file(repo_path, prd_path):
#     """Read data from a CSV file."""
#     try:
#         if os.path.exists(prd_path):
#             df = pd.read_csv(prd_path)
#             #st.info("Data loaded from local storage.")
#         else:
#             # Initial load from a repository, as a fallback (if needed)
#             df = pd.read_csv(repo_path)  # Replace with your default CSV
#             df.to_csv(prd_path, index=False)  # Save to local environment
#             #st.info("Data loaded from repository and saved to local storage.")
#         return df
#     except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
#         st.error(f"Error loading file: {repo_path} - {str(e)}")
#         return pd.DataFrame()
#     except Exception as e:
#         st.error(f"Unexpected error: {e}")
#         return pd.DataFrame()

def get_filtered_words(test_id):
    """Read and filter the WordsList.csv file based on the TestID."""
    try:
        df_words = cm.read_csv_file(cm.WORDS_CSV_FILE_PATH, cm.prd_WordsList_path)
        filtered_words = df_words[df_words['TestID'] == int(test_id)]
        return filtered_words, df_words  # Return both the filtered and full DataFrame
    except Exception as e:
        st.error(f"Error filtering WordsList.csv: {e}")
        return pd.DataFrame(), pd.DataFrame()

def show_editable_table_with_delete(df, full_df, test_id):
    """Display the editable table with AgGrid, including delete functionality, and return the edited DataFrame."""
    gb = GridOptionsBuilder.from_dataframe(df)
    
    # Enable cell editing
    gb.configure_default_column(editable=True)
    
    # Configure pagination and selection
    gb.configure_selection('single', use_checkbox=True)
    
    # Build grid options
    grid_options = gb.build()

    # Display the grid
    grid_return = AgGrid(
        df, 
        gridOptions=grid_options, 
        update_mode=GridUpdateMode.MODEL_CHANGED | GridUpdateMode.SELECTION_CHANGED
    )
    
    # Extract selected rows
    selected_rows = grid_return.get('selected_rows', [])
    # Debugging output
    # st.write("Selected Rows:", selected_rows)  
    
    # Make the button always visible
    delete_button_visible = False
    
    # Check if selected_rows is non-empty and contains valid data
    if isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty:
        
        # Ensure the first element of selected_rows is a dictionary and contains 'WordID'
        if 'WordID' in selected_rows.columns:  # note selected_rows[0] or selected_rows.columns
            delete_button_visible = True  # Indicate that the delete button should be visible

            word_id_to_delete = selected_rows.iloc[0]['WordID']
            
            # Display the delete button
            if st.button("Delete Selected Word"):
                try:
                    # Filter out the row with the selected WordID
                    full_df = full_df[full_df['WordID'] != word_id_to_delete]
                    
                    # Save the updated DataFrame back to the CSV
                    full_df.to_csv(cm.prd_WordsList_path, index=False)
                    
                    st.success(f"Word ID {word_id_to_delete} has been deleted successfully!")
                    st.rerun()  # Refresh the page to reflect the changes
                except Exception as e:
                    st.error(f"Error deleting word: {e}")
        else:
            st.error("No 'WordID' found in the selected row or selected row is not valid.")
    
    # Display the delete button even if no row is selected (for testing visibility)
    if not delete_button_visible:
        # Using HTML to customize the warning message style
        st.markdown(
            "<span style='color:gray; font-size:12pt; font-style:italic;'>Please select a row to enable deletion.</span>",
            unsafe_allow_html=True
        )
    
    # Get the edited DataFrame after changes
    edited_df = grid_return['data']
    return edited_df

def update_words_csv(updated_df, full_df, test_id):
    """Update the WordsList.csv file with the edited DataFrame for the specific TestID."""
    try:
        # Drop the rows with the current TestID from the original DataFrame
        full_df = full_df[full_df['TestID'] != int(test_id)]
        
        # Append the updated rows for the current TestID
        full_df = pd.concat([full_df, updated_df], ignore_index=True)
        
        # Debugging: Display unique Test IDs to ensure data integrity
        st.write(f'Unique Test IDs = {full_df["TestID"].unique()}')

        # Save the updated DataFrame back to the CSV
        full_df.to_csv(cm.prd_WordsList_path, index=False)
        st.success("WordsList.csv has been updated successfully!")
    except Exception as e:
        st.error(f"Error updating WordsList.csv: {e}")

def insert_new_word(new_word, language_code, new_WordPhonetic, new_WordDescription, new_WordImageLink, full_df, test_id):
    """Insert a new word into the WordsList.csv file."""
    if not new_word or not new_WordDescription:
        st.error("Fields New words and Word Description must be filled out.")
        return
    
    try:
        # Auto-generate the WordID as max WordID + 1
        new_word_id = full_df['WordID'].max() + 1

        # Create a new row for the new word
        new_row = {
            'WordID': new_word_id,
            'TestID': int(test_id),
            'Word': new_word,
            'LanguageCode': language_code,
            'WordPhonetic': new_WordPhonetic,
            'Description': new_WordDescription,
            'Image': new_WordImageLink,
        }

        # Convert the new row to a DataFrame
        new_row_df = pd.DataFrame([new_row])

        # Concatenate the new row with the full DataFrame
        full_df = pd.concat([full_df, new_row_df], ignore_index=True)

        # Save the updated DataFrame back to the CSV
        full_df.to_csv(cm.prd_WordsList_path, index=False)
        st.success("New word has been added successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Error inserting new word: {e}")

# Display the insert form
def show_insert_form(language_code, full_df, test_id):     
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        new_word = st.text_input(f"New word ({language_code})*")   
    with col2:
        new_WordDescription = st.text_input("Word Description*")
    with col3:
        new_WordPhonetic = st.text_input("Phonetic or Examples")
    with col4:
        new_WordImageLink = st.text_input("Image Link") 
    if st.button("Add Word"):
        insert_new_word(new_word, language_code, new_WordPhonetic, new_WordDescription, new_WordImageLink, full_df, test_id)

def show_question_editor():
    """Show the editor for a specific TestID."""
    selected_test = st.session_state.get("selected_test")

    if not selected_test:
        st.write("No TestID selected.")
        return

    test_id = selected_test
    df_tests = cm.read_csv_file(cm.TESTS_CSV_FILE_PATH, cm.prd_TestsList_path)

    # Filter the DataFrame for the selected TestID in TestsList.csv
    test_info = df_tests[df_tests['TestID'] == int(test_id)]
    if test_info.empty:
        st.write(f"No data found for TestID {test_id} in TestsList.csv")
        return
    
    # Lookup the corresponding test name & TestLanguage for the selected TestID
    language_code = test_info.iloc[0]['TestLanguage']  # 'TestsList\TestLanguage' == 'WordsList\LanguageCode' need to fix in TestsList csv file later.
    test_name = test_info.iloc[0]['TestName']  # get the corresponding 'TestName' from TestsList
    st.write(f"#### *Test ID {int(test_id)} - {test_name}*")

    # Get the filtered words data and the full DataFrame from WordsList.csv
    df_words, full_df = get_filtered_words(test_id)

    if df_words.empty:
        st.error(f"No words data found for TestID {int(test_id)} - {test_name} in Data")
        # Display the insert form
        st.write("# Add a New Word")
        show_insert_form(language_code, full_df, test_id)
        if st.button("🔙 Back"):
            st.session_state.page = 'table'
            st.rerun()
        return

    # Display the insert form
    st.write("### Add a New Word")
    show_insert_form(language_code, full_df, test_id)

    # Display the editable table with delete functionality
    st.write("### Edit Words")
    edited_df = show_editable_table_with_delete(df_words, full_df, test_id)

    #col1, col2, col3 = st.columns(3)
    col = st.columns([1, 2, 1])
    with col[0]:
        # Use the placeholder to insert the actual button, applying the custom CSS class
        if st.button("🔙 Back", key="back"):
            st.session_state.page = 'table'
            st.rerun()
    with col[1]:
        st.write(" ")
    with col[2]:
        # Update the CSV file when the button is clicked
        if st.button("Update"):
            update_words_csv(edited_df, full_df, test_id)

# Ensure 'page' is initialized
if "page" not in st.session_state:
    st.session_state["page"] = "table"  # Default to the main table
elif st.session_state.page == 'edit_question':
    show_question_editor()
