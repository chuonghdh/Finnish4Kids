import streamlit as st

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

def main():

    set_custom_css()
    
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
        st.session_state.page = 'table'
        st.session_state.url = 'Manage_Test/edit_test.py'
        st.rerun()  # Reload the page to reflect the new selection
    if st.sidebar.button('Backup tests data'):
        st.session_state.page = 'backup'
        st.session_state.url = 'Manage_Test/backup_tests.py'
        st.rerun()  # Reload the page to reflect the new selection

    # Display the selected page
    if "page" in st.session_state:
        st.write(f"Selected Page: {st.session_state.page}") #IMPORTANT FOR DEBUG
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
