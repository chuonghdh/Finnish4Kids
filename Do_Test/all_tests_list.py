import streamlit as st
import pandas as pd
import os
import requests
import common as cm
from PIL import Image
from io import BytesIO
import logging
from Do_Test.define_metadata import main_define_metadata
from Do_Test.do_test import main_do_test
from Do_Test.result_page import main_result_page
from Do_Test.gen_audio import create_full_audio
#from Do_Test.gen_audio import regen_full_audio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for file paths
IMAGE_SIZE = 80  # Set this to the desired thumbnail size (e.g., 60 pixels)

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

def get_filtered_words(test_id):
    """Read and filter the WordsList.csv file based on the TestID."""
    try:
        df_words = cm.read_csv_file(cm.WORDS_CSV_FILE_PATH, cm.prd_WordsList_path)
        filtered_words = df_words[df_words['TestID'] == int(test_id)]
        return filtered_words  # Return the filtered DataFrame
    except Exception as e:
        st.error(f"Error filtering WordsList.csv: {e}")
        return pd.DataFrame()

@st.dialog("Create Audio File")
def show_dialog(test_name, test_id):
    st.write(f"Test {test_name} did not have Audio File yet.")
    st.write(f"Do you want to create the Audio?")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Back"):
            st.rerun()
    with col2:
        if st.button("Create Audio"):
            st.write(f"Creating audio for {test_id}-{test_name}")           
            # read csv Filter df
            df = get_filtered_words(test_id)

            # Create Audio folder in prd environment if it does not exist
            if not os.path.exists(cm.prd_Audio_path):
                os.makedirs(cm.prd_Audio_path)
            if not os.path.exists(cm.prd_Temp_path):
                os.makedirs(cm.prd_Temp_path)
            else:
                # If the folder exists, clear it
                cm.clear_files_in_folder(cm.prd_Temp_path)
            audio_name = f"TestID_{test_id}"
            # create and save audio
            with st.spinner('Please wait...'):
                create_full_audio(audio_name, df, cm.prd_Audio_path)
            st.success(f"Audio for {test_id}-{test_name} is created successfully")
    

def show_test_list(df):
    st.write("### Select your test")

    for index, row in df.iterrows():
        cols = st.columns([1.2, 1.5, 1.5, 1, 1])  # Adjust column widths

        # Check if the image URL is valid; if not, use the placeholder image
        image_url = row["Image"]
        img = fetch_and_resize_image(image_url if image_url else cm.PLACEHOLDER_IMAGE, IMAGE_SIZE)

        # Display row data with improved layout
        cols[0].image(img)
        cols[1].write(f"{row['TestName']} ({row['TestLanguage']})")
        #cols[2].write(row["TestLanguage"])
        cols[2].write(row["TestDescription"])
        if cols[3].button('Listen', key=f"button_listen_{index}"):
            st.session_state.selected_test = row['TestID']
            file_path = f"{cm.prd_Audio_path}/TestID_{row['TestID']}.mp3"
            if os.path.exists(file_path):
                st.audio(file_path, format="audio/mpeg", autoplay=True, loop=True)
            else:
                show_dialog(row["TestName"], row["TestID"])
            
            #st.rerun()
        # Add button to the last column and handle click
        if cols[4].button('Do Test', key=f"button_DoTest_{index}"):
            st.session_state.selected_test = row['TestID']
            st.session_state.page = 'prep_test'
            st.rerun()

def show_test_id(test_id):
    """Display the TestID in a pop-up frame."""
    st.write(f"**TestID:** {test_id}")

def main_show_test_list():
    """Main function to display the test list page."""
    
    if 'page' not in st.session_state:
        st.session_state.page = 'test_list'
    if 'selected_test' not in st.session_state:
        st.session_state.selected_test = None

    #"""Page routing logic."""
    if st.session_state.page == 'test_list':
        st.title("Test List")
        # Load and display the test list
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

main_show_test_list()
