import streamlit as st
import pandas as pd
import logging
import os
import common as cm
from Do_Test.gen_audio import create_full_audio
from Do_Test.gen_audio import regen_full_audio

# Setup logging
#logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger(__name__)

@st.dialog("Test data")
def show_dialog(df):
    st.write(df)

# Function to display folder structure with expanders
def display_directory_tree(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        
        # Create an expander for the current folder
        with st.expander(f"{indent}📁 {os.path.basename(root)}/", expanded=False):
            subindent = ' ' * 4 * (level + 1)
            # Display all files in the current folder
            for file in files:
                st.write(f'{subindent}📄 {file}')

def show_test_list(df):
    st.write("### Select your test")

    for index, row in df.iterrows():
        cols = st.columns([0.05, 0.15, 0.2, 0.3, 0.2, 0.1])  # Adjust column widths
        cols[0].write(row['TestID'])
        cols[1].write(f"{row['TestName']} ({row['TestLanguage']})")
        cols[2].write(row["TestDescription"])
        with cols[3]:
            button_label=""
            audio_name = f"TestID_{row['TestID']}"
            file_path = f"{cm.prd_Audio_path}/{audio_name}.mp3"
            if os.path.exists(file_path):
                st.audio(file_path, format="audio/mpeg", autoplay=False, loop=False)
                button_label ="Regen Audio"
            else:
                st.write(" Don't have audio yet!")
                button_label ="Create Audio"
        # Add button to the last column and handle click
        if cols[4].button(button_label, key=f"button_GenAudio_{index}"):
            df_word = cm.read_csv_file(cm.WORDS_CSV_FILE_PATH, cm.prd_WordsList_path)
            filtered_df = df_word[df_word['TestID'] == int(row['TestID'])]
            regen_full_audio(audio_name, filtered_df, cm.prd_Audio_path)
            st.rerun()
        if cols[5].button("Delete", key=f"button_Delete_{index}"):
            cm.delete_file(file_path)
            st.rerun()

st.title('Back up data')

tab1, tab2, tab3 = st.tabs(["Text Data", "Audio Data", "Edit Audio"])
with tab1:
    st.write('This is a page to download all data from host')

    # Set the directory where your CSV files are stored
    folder_path = "prd_Data"  # Change this to your CSV directory path

    # Loop through each file in the directory
    if os.path.exists(folder_path):  # Check if the folder exists and is a directory
        for filename in os.listdir(folder_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(folder_path, filename)

                # Read the file contents with UTF-8 BOM encoding
                with open(file_path, "r", encoding="utf-8-sig") as file:
                    file_content = file.read()

                # Convert the content back to bytes for the download button
                file_bytes = file_content.encode("utf-8-sig")

                # Create a download button for each file
                st.download_button(
                    label=f"Download {filename}",
                    data=file_bytes,
                    file_name=filename,
                    mime="text/csv"
                )
    else: 
        st.warning(f"Cannot find '{folder_path}' folder")
with tab2:
    # Specify the path of the directory you want to display
    directory_path = cm.prd_Data_path  # Current directory or specify a custom path
    display_directory_tree(directory_path)
with tab3:
    df = cm.read_csv_file(cm.TESTS_CSV_FILE_PATH, cm.prd_TestsList_path)
    
    show_test_list(df)

