import streamlit as st
import pandas as pd
from pydub import AudioSegment
import os
import base64
from gtts import gTTS
import io
import glob
import common as cm
from googletrans import Translator

#WORDS_CSV_FILE_PATH = 'Data/WordsList.csv'
#prd_WordsList_path = 'prd_Data/prd_WordsListData.csv'
#prd_Audio_path = 'prd_Data/prd_Audio'
#prd_Temp_path = 'prd_Data/prd_Temp'

def delete_files(folder_path, file_type):
    files_to_delete = glob.glob(os.path.join(folder_path, file_type))
    print(files_to_delete)
    for file in files_to_delete:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")

def gen_audio(word, lang_code,is_slow):
    tts = gTTS(text=word, lang=lang_code, slow=is_slow)
    audio_fp = io.BytesIO()  # Create an in-memory byte stream
    tts.write_to_fp(audio_fp)  # Write audio to the stream
    audio_fp.seek(0)  # Move the pointer to the start of the stream

    # Encode audio data to base64
    audio_bytes = audio_fp.read()
    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    return audio_b64

def save_audio_b64_to_file(audio_b64, file_path):
    # Decode the base64 string back to bytes
    audio_bytes = base64.b64decode(audio_b64)
    
    # Write the bytes to a file
    with open(file_path, "wb") as audio_file:
        audio_file.write(audio_bytes)

# Function to create audio with Finnish and Vietnamese, including silences
def create_speech_with_pauses(word_text, desc_text, word_lang_code, desc_lang_code, audio_name, word_id, save_path):
    # Generate Finnish speech (slow down by 60%)
    word_response = gen_audio(word_text, word_lang_code, is_slow=True)
    word_filename = f"{save_path}/word_{audio_name}_{word_id}.mp3"
    save_audio_b64_to_file(word_response, word_filename)
    word_audio = AudioSegment.from_file(word_filename)

    # Generate Vietnamese speech
    desc_response = gen_audio(desc_text, desc_lang_code, is_slow=False)
    desc_filename = f"{save_path}/desc_{audio_name}_{word_id}.mp3"
    save_audio_b64_to_file(desc_response, desc_filename)
    desc_audio = AudioSegment.from_file(desc_filename)

    # Create silence segments
    one_second_silence = AudioSegment.silent(duration=1000)
    one_and_half_second_silence = AudioSegment.silent(duration=1500)

    # Sequence: Finnish -> 1s silence -> Vietnamese -> 1.5s silence -> repeat
    combined_audio = (
        word_audio + one_second_silence +
        desc_audio + one_and_half_second_silence +
        word_audio + one_second_silence +
        desc_audio + one_and_half_second_silence
    )

    return combined_audio

# Initialize the translator
translator = Translator()
def detect_language(data):
    text = data
    detected_lang = translator.detect(text)
    return detected_lang.lang

# Function to create full audio for a given TestID
def create_full_audio(audio_name, df, save_path):

    # detect Word lang and Descr lang
    word_data = df["Word"].str.cat(sep=', ')
    desc_data = df["Description"].str.cat(sep=', ')
    word_lang_code = detect_language(word_data)
    desc_lang_code = detect_language(desc_data)
    st.write(f"learn {word_lang_code} by {desc_lang_code}")       

    final_audio_filename = f"{audio_name}.mp3"
    full_path_to_file = f"{save_path}/{final_audio_filename}"
    if os.path.exists(full_path_to_file):
        return
    
    combined_audio = AudioSegment.silent(duration=0)  # Start with empty audio

    for index, row in df.iterrows():
        word_text = row['Word']
        desc_text = row['Description']
        word_id = int(row['WordID'])

        # Create audio for this row
        row_audio = create_speech_with_pauses(word_text, desc_text, word_lang_code, desc_lang_code, audio_name, word_id,cm.prd_Temp_path)

        # Add to the combined audio
        combined_audio += row_audio

    # Export the final combined audio for the TestID group
    combined_audio.export(f"{save_path}/{final_audio_filename}", format='mp3')
    cm.clear_files_in_folder(cm.prd_Temp_path)
    return final_audio_filename

def regen_full_audio(audio_name, df, save_path):
    final_audio_filename = f"{audio_name}.mp3"
    full_path_to_file = f"{save_path}/{final_audio_filename}"
    if os.path.exists(full_path_to_file):
        cm.delete_file(full_path_to_file)
    create_full_audio(audio_name, df, save_path)
    