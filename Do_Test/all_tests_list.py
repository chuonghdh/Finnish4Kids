# ============================================================================
# IMPORTS
# ============================================================================
import streamlit as st
import pandas as pd
import os
import logging
from PIL import Image
from io import BytesIO
import requests

import common as cm
from Do_Test.define_metadata import main_define_metadata
from Do_Test.do_test import main_do_test
from Do_Test.result_page import main_result_page
from Do_Test.gen_audio import create_full_audio


# ============================================================================
# SETUP & CONFIGURATION
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IMAGE_SIZE = 80  # Thumbnail size in pixels


# ============================================================================
# IMAGE HANDLING
# ============================================================================

@st.cache_data
def fetch_and_resize_image(url, size):
    """Fetch an image from a URL and resize it to the given size."""
    try:
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content))
        img.thumbnail((size, size))
        return img
    except requests.RequestException as e:
        logger.error(f"Error fetching image from {url}: {e}")
        return Image.open(cm.PLACEHOLDER_IMAGE).resize((size, size))
    except Exception as e:
        logger.error(f"Error processing image from {url}: {e}")
        return Image.open(cm.PLACEHOLDER_IMAGE).resize((size, size))


# ============================================================================
# DATA HANDLING
# ============================================================================

def get_filtered_words(test_id):
    """Read and filter the WordsList.csv file based on the TestID."""
    try:
        df_words = cm.read_csv_file(cm.WORDS_CSV_FILE_PATH, cm.prd_WordsList_path)
        filtered_words = df_words[df_words['TestID'] == int(test_id)]
        return filtered_words
    except Exception as e:
        st.error(f"Error filtering WordsList.csv: {e}")
        return pd.DataFrame()


# ============================================================================
# AUDIO FILE HANDLING
# ============================================================================

@st.dialog("Create Audio File")
def show_audio_creation_dialog(test_name, test_id):
    """Dialog to confirm and create audio file for a test."""
    st.write(f"Test {test_name} did not have Audio File yet.")
    st.write(f"Do you want to create the Audio?")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Back"):
            st.rerun()
    with col2:
        if st.button("Create Audio"):
            st.write(f"Creating audio for {test_id}-{test_name}")           
            
            # Read and filter words for this test
            df = get_filtered_words(test_id)

            # Create Audio and Temp folders if they don't exist
            if not os.path.exists(cm.prd_Audio_path):
                os.makedirs(cm.prd_Audio_path)
            if not os.path.exists(cm.prd_Temp_path):
                os.makedirs(cm.prd_Temp_path)
            else:
                # Clear temp folder if it exists
                cm.clear_files_in_folder(cm.prd_Temp_path)
            
            audio_name = f"TestID_{test_id}"
            
            # Create and save audio
            with st.spinner('Please wait...'):
                create_full_audio(audio_name, df, cm.prd_Audio_path)
            
            st.success(f"Audio for {test_id}-{test_name} is created successfully")


def handle_listen_button(test_id, test_name):
    """Handle play audio button - play or create audio file."""
    file_path = f"{cm.prd_Audio_path}/TestID_{test_id}.mp3"
    
    if os.path.exists(file_path):
        st.audio(file_path, format="audio/mpeg", autoplay=True, loop=True)
    else:
        show_audio_creation_dialog(test_name, test_id)


# ============================================================================
# UI & DISPLAY COMPONENTS
# ============================================================================

def display_test_row(index, row):
    """Display a single test row in the test list."""
    cols = st.columns([1.2, 1.5, 1.5, 1, 1])

    # Fetch and display image
    image_url = row["Image"]
    img = fetch_and_resize_image(image_url if image_url else cm.PLACEHOLDER_IMAGE, IMAGE_SIZE)
    cols[0].image(img)

    # Display test information
    cols[1].write(f"{row['TestName']} ({row['TestLanguage']})")
    cols[2].write(row["TestDescription"])

    # Listen button
    if cols[3].button('Listen', key=f"button_listen_{index}"):
        st.session_state.selected_test = row['TestID']
        handle_listen_button(row['TestID'], row["TestName"])

    # Do Test button
    if cols[4].button('Do Test', key=f"button_DoTest_{index}"):
        st.session_state.selected_test = row['TestID']
        st.session_state.page = 'prep_test'
        st.rerun()


def show_test_list(df):
    """Display the complete test list with interactive options."""
    # Sort by TestID in descending order (bigger numbers first)
    df = df.sort_values('TestID', ascending=False)
    
    st.write("### Select your test")

    for index, row in df.iterrows():
        display_test_row(index, row)


# ============================================================================
# PAGE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'page' not in st.session_state:
        st.session_state.page = 'test_list'
    if 'selected_test' not in st.session_state:
        st.session_state.selected_test = None


# ============================================================================
# PAGE ROUTING
# ============================================================================

def route_pages():
    """Route to the appropriate page based on session state."""
    if st.session_state.page == 'test_list':
        st.title("Test List")
        df = cm.read_csv_file(cm.TESTS_CSV_FILE_PATH, cm.prd_TestsList_path)
        if not df.empty:
            show_test_list(df)
        else:
            st.write("No data available.")
    
    elif st.session_state.page == 'prep_test':
        main_define_metadata()
    
    elif st.session_state.page == 'do_test':
        main_do_test()
    
    elif st.session_state.page == 'result_page':
        main_result_page()


# ============================================================================
# MAIN LOGIC
# ============================================================================

def main_show_test_list():
    """Main function to orchestrate the test list page."""
    initialize_session_state()
    route_pages()


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main_show_test_list()

