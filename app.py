import streamlit as st
import pandas as pd
import os
import common as cm
import time

def set_custom_css():
    """Set custom CSS for wider table, row borders, and hover effects."""
    st.markdown(
        """
        <style>
        .streamlit-expanderHeader {
            font-size: 0.2rem;
        }
        .block-container {
            max-width: 900px;
            padding: 0.2rem 0.2rem;
        }
        .stButton>button {
            width: 100%;
        }
        .table-header {
            display: flex;
            background-color: #f0f0f0;
            padding: 2px;
            font-weight: bold;
            border-bottom: 1px solid #ccc;
            margin-bottom: 2px;
        }
        .table-row {
            display: flex;
            padding: 0.2px;
            border: 1px solid lightgray;
            margin-bottom: 1px;
            transition: background-color 0.3s ease;
        }
        .table-row:hover {
            background-color: #f0f0f0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Define the correct passkey
correct_passkey = "class4vn"

def main():
    prd_data_path = 'prd_Data' # prd_Data file only available in PRD evironment
    if not os.path.exists(prd_data_path):
        cm.initialize_folder('prd_Data')
        cm.initialize_data()
    
    set_custom_css()

    # Create a state variable to keep track of whether the passkey has been validated
    if 'passkey_validated' not in st.session_state:
        st.session_state.passkey_validated = False
    
    # Define pages with their titles and file paths
    pages = {
        "Do Your Test": [
            ("List of all tests", "Do_Test/all_tests_list.py"),
        ],
        "Manage Your Test": [
            ("Edit current test", "Manage_Test/edit_test.py"),
            ("Backup tests data", "Manage_Test/backup_tests.py"),
        ]
    }

    # Sidebar navigation
    st.sidebar.title("Navigation")
    if st.sidebar.button('List of all tests'):
        st.session_state.page = 'test_list'
        st.session_state.url = 'Do_Test/all_tests_list.py'
        st.rerun()  # Reload the page to reflect the new selection
    if st.sidebar.button('Edit current test'):
        st.session_state.page  = 'input_passkey'
        st.rerun()
    if st.sidebar.button('Backup tests data'):
        st.session_state.page = 'backup'
        st.session_state.url = 'Manage_Test/backup_tests.py'
        st.rerun()  # Reload the page to reflect the new selection

    # Display the selected page
    if "page" in st.session_state:
        if st.session_state.page  == 'input_passkey':  
            st.write("###Warning###")
            st.subheader("You need passkey to edit the test:")
            passkey = st.text_input('Enter passkey:')
            if st.button('Submit'):
                if passkey.lower() == correct_passkey.lower():
                    st.session_state.passkey_validated = True
                    st.success("Passkey validated!")
                    st.session_state.page = 'table'
                    st.session_state.url = 'Manage_Test/edit_test.py'
                    time.sleep(0.8)
                    st.rerun()  # Reload the page to reflect the new selection
                else:
                    st.warning("Wrong passkey. Please try again.")
        else:
            st.write(f"Selected Page: {st.session_state.page}") #IMPORTANT FOR DEBUG
            st.session_state.passkey_validated = False
            # Open the file with the correct encoding (usually UTF-8)
            with open(st.session_state.url, 'r', encoding='utf-8') as f:
                code = f.read()
            exec(code, globals())  # Execute the selected page
    else:
        st.session_state.page = 'test_list'
        st.session_state.url = 'Do_Test/all_tests_list.py'
        st.rerun()

if __name__ == "__main__":
    main()
