import streamlit as st
import pandas as pd
import os
import requests
#import common as cm
from googletrans import Translator
from PIL import Image
from io import BytesIO
import logging
from Do_Test.define_metadata import main_define_metadata
from Do_Test.do_test import main_do_test
from Do_Test.result_page import main_result_page
from Do_Test.gen_audio import create_full_audio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for file paths
TESTS_CSV_FILE_PATH = 'Data/TestsList.csv'  # Adjust the path if necessary
WORDS_CSV_FILE_PATH = 'Data/WordsList.csv'
PLACEHOLDER_IMAGE = "Data/image/placeholder_image.png"
IMAGE_SIZE = 80  # Set this to the desired thumbnail size (e.g., 60 pixels)

## File path for the CSV in the Streamlit environment
prd_TestsList_path = 'prd_Data/prd_TestsListData.csv'
prd_WordsList_path = 'prd_Data/prd_WordsListData.csv'
prd_Audio_path = 'prd_Data/prd_Audio'
prd_Temp_path = 'prd_Data/prd_Temp'

#@st.cache_data
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
        return Image.open(PLACEHOLDER_IMAGE).resize((size, size))
    except Exception as e:
        logger.error(f"Error processing image from {url}: {e}")
        return Image.open(PLACEHOLDER_IMAGE).resize((size, size))

def get_filtered_words(test_id):
    """Read and filter the WordsList.csv file based on the TestID."""
    try:
        df_words = read_csv_file(WORDS_CSV_FILE_PATH, prd_WordsList_path)
        filtered_words = df_words[df_words['TestID'] == int(test_id)]
        return filtered_words  # Return the filtered DataFrame
    except Exception as e:
        st.error(f"Error filtering WordsList.csv: {e}")
        return pd.DataFrame()

# Initialize the translator
translator = Translator()
def detect_language(data):
    text = data
    detected_lang = translator.detect(text)
    return detected_lang.lang

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
            # detect Word lang and Descr lang
            word_data = df["Word"].str.cat(sep=', ')
            desc_data = df["Description"].str.cat(sep=', ')
            word_lang_code = detect_language(word_data)
            desc_lang_code = detect_language(desc_data)
            st.write(f"word_lang_code ={word_lang_code} ; desc_lang_code ={desc_lang_code}")
            # Create Audio folder in prd environment if it does not exist
            if not os.path.exists(prd_Audio_path):
                os.makedirs(prd_Audio_path)
            if not os.path.exists(prd_Temp_path):
                os.makedirs(prd_Temp_path)
            # create and save audio
            with st.spinner('Please wait...'):
                create_full_audio(test_id, df, word_lang_code, desc_lang_code, path=prd_Audio_path)
            st.success(f"Audio for {test_id}-{test_name} is created successfully")
    

def show_test_list(df):
    st.write("### Select your test")

    for index, row in df.iterrows():
        cols = st.columns([1.2, 1.5, 1.5, 1, 1])  # Adjust column widths

        # Check if the image URL is valid; if not, use the placeholder image
        image_url = row["Image"]
        img = fetch_and_resize_image(image_url if image_url else PLACEHOLDER_IMAGE, IMAGE_SIZE)

        # Display row data with improved layout
        cols[0].image(img)
        cols[1].write(f"{row['TestName']} ({row['TestLanguage']})")
        #cols[2].write(row["TestLanguage"])
        cols[2].write(row["TestDescription"])
        if cols[3].button('Listen', key=f"button_listen_{index}"):
            st.session_state.selected_test = row['TestID']
            file_path = f"{prd_Audio_path}/TestID_{row['TestID']}.mp3"
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
        df = read_csv_file(TESTS_CSV_FILE_PATH, prd_TestsList_path)
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
