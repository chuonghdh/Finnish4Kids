# ============================================================================
# IMPORTS
# ============================================================================
import streamlit as st
import pandas as pd
import os
import time

import common as cm


# ============================================================================
# SETUP & CONFIGURATION
# ============================================================================

# Authentication
CORRECT_PASSKEY = "class4vn"

# Paths
PRD_DATA_PATH = 'prd_Data'


# ============================================================================
# STYLING
# ============================================================================

def set_custom_css():
    """Set custom CSS for wider layout, table styling, and hover effects."""
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


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_environment():
    """Initialize production data folder and common data if needed."""
    if not os.path.exists(PRD_DATA_PATH):
        cm.initialize_folder(PRD_DATA_PATH)
        cm.initialize_data()


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'passkey_validated' not in st.session_state:
        st.session_state.passkey_validated = False


# ============================================================================
# AUTHENTICATION
# ============================================================================

def display_passkey_form():
    """Display passkey entry form for test editing access."""
    st.write("### Warning ###")
    st.subheader("You need passkey to edit the test:")
    
    passkey = st.text_input('Enter passkey:')
    
    if st.button('Submit'):
        if passkey.lower() == CORRECT_PASSKEY.lower():
            st.session_state.passkey_validated = True
            st.success("Passkey validated!")
            st.session_state.page = 'table'
            st.session_state.url = 'Manage_Test/edit_test.py'
            time.sleep(0.8)
            st.rerun()
        else:
            st.warning("Wrong passkey. Please try again.")


# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

def display_sidebar_navigation():
    """Display navigation buttons in the sidebar."""
    st.sidebar.title("Navigation")
    
    if st.sidebar.button('List of all tests'):
        st.session_state.page = 'test_list'
        st.session_state.url = 'Do_Test/all_tests_list.py'
        st.rerun()
    
    if st.sidebar.button('Edit current test'):
        st.session_state.page = 'input_passkey'
        st.rerun()
    
    if st.sidebar.button('Backup tests data'):
        st.session_state.page = 'backup'
        st.session_state.url = 'Manage_Test/backup_tests.py'
        st.rerun()


# ============================================================================
# PAGE ROUTING & EXECUTION
# ============================================================================

def load_and_execute_page(page_url):
    """Load and execute a page file dynamically."""
    with open(page_url, 'r', encoding='utf-8') as f:
        code = f.read()
    exec(code, globals())


def route_page(current_page):
    """Route to the appropriate page based on session state."""
    if current_page == 'input_passkey':
        display_passkey_form()
    else:
        # Debug info
        st.write(f"Selected Page: {current_page}")
        st.session_state.passkey_validated = False
        
        # Load and execute the page
        load_and_execute_page(st.session_state.url)


# ============================================================================
# MAIN LOGIC
# ============================================================================

def main():
    """Main application orchestrator."""
    # Initialize environment
    initialize_environment()
    
    # Apply custom styling
    set_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Display sidebar navigation
    display_sidebar_navigation()
    
    # Route to appropriate page
    if "page" in st.session_state:
        route_page(st.session_state.page)
    else:
        # Set default page if none is selected
        st.session_state.page = 'test_list'
        st.session_state.url = 'Do_Test/all_tests_list.py'
        st.rerun()


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()

