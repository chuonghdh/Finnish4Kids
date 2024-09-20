import streamlit as st
import pandas as pd
import os
import requests
from PIL import Image
from io import BytesIO
import logging
from PIL import Image
import random
from gtts import gTTS
import tempfile
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval
import base64
import pyperclip
import io
import json
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for file paths
TESTS_CSV_FILE_PATH = 'Data/TestsList.csv'
WORDS_CSV_FILE_PATH = 'Data/WordsList.csv'
ATTEMPTDATA_CSV_FILE_PATH = 'Data/AttemptData.csv'
PLACEHOLDER_IMAGE = "Data/image/placeholder_image.png"
IMAGE_SIZE = 100  # Set this to the desired thumbnail size

# File path for the CSV in the Streamlit environment
prd_TestsList_path = 'prd_Data/prd_TestsListData.csv'
prd_WordsList_path = 'prd_Data/prd_WordsListData.csv'
prd_AttemptData_path = 'prd_Data/prd_AttemptData.csv'

st.markdown(
    """
    <style>
    .center-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Convert the sound file to base64
def get_base64_sound(file_path):
    with open(file_path, "rb") as sound_file:
        data = sound_file.read()
        return base64.b64encode(data).decode()

# Convert 'beep-beep.wav' and 'cheerful.wav' files to base64 strings
beep_sound_base64 = get_base64_sound("Data/sound/beep-beep.wav") #Kalam requirement "Data/sound/beep-beep2.wav"
cheerful_sound_base64 = get_base64_sound("Data/sound/cheerful.wav")

@st.cache_data
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

def get_filtered_words(test_id):
    """Read and filter the WordsList.csv file based on the TestID."""
    try:
        df_words = read_csv_file(WORDS_CSV_FILE_PATH, prd_WordsList_path)
        filtered_words = df_words[df_words['TestID'] == int(test_id)]
        return filtered_words  # Return the filtered DataFrame
    except Exception as e:
        st.error(f"Error filtering WordsList.csv: {e}")
        return pd.DataFrame()

def set_words_order(df, order_type):
    number_of_rows = len(df) 
    if order_type == "sequence":
        order = list(range(1, number_of_rows + 1)) # Create a sequence list from 1 to number_of_rows
    elif order_type == "random":
        order = random.sample(range(1, number_of_rows + 1), number_of_rows) # Create a random list from 1 to number_of_rows without duplicates
    else:
        order = list(range(1, number_of_rows + 1))
        st.warning("Invalid order_type. Must be 'sequence' or 'random'. return default order is 'sequence'")
    df.insert(0, 'order', order)
    return df

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

# Word matching function using java script to process
def word_matching(word, tid):
    word_score = len(word) - word.count(" ")
    # Create an HTML component with JavaScript to handle input, color, and deletion of text
    components.html(
        f"""
        <html>
            <head>
                <style>
                    /* Increase font size to 14px */
                    body {{
                        font-size: 18px;
                    }}

                    /* Align display area and score on the same line */
                    #container {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 0px;
                        margin-left: 0px;
                    }}

                    #displayArea {{
                        flex: 1;
                        text-align: left;
                        margin-left: 5px;
                        font-family: 'Source Sans Pro', sans-serif;
                        font-size: 25px;
                        color: #39e75f;
                    }}

                    #scoreArea {{
                        flex-shrink: 0;
                        text-align: right;
                        margin-left: 20px;
                        font-family: 'Source Sans Pro', sans-serif;
                        font-size: 15px;
                        color: #474a5c;
                        line-height: 1.6;
                    }}

                    /* Center input box and add margin to the top */
                    #textInput {{
                        width: 100%;
                        height: 30px;
                        margin-top: 2px;
                        text-align: left;
                        font-family: 'Source Sans Pro', sans-serif;
                        font-size: 20px;
                        border: 2px solid #39e75f; 
                        background-color: #39e75f;
                        border-radius: 5px;  /* Rounded corners */
                    }}
                </style>
            </head>
            <body>
                <div id="container">
                    <p id="displayArea">{''.join('_' if c == ' ' else '-' for c in word)}</p> <!-- Display underscores for spaces and dashes for other characters -->
                    <p id="scoreArea">Score: {word_score}</p> <!-- Display the initial word score -->
                </div>
                <input type="text" id="textInput" placeholder="Enter some text" oninput="checkText()" />

                <audio id="alarmSound" src="data:audio/wav;base64,{beep_sound_base64}" preload="auto"></audio> <!-- Beep alarm sound -->
                <audio id="cheerfulSound" src="data:audio/wav;base64,{cheerful_sound_base64}" preload="auto"></audio> <!-- Cheerful sound -->

                <script>
                    // JavaScript variables
                    const word = "{word}".toLowerCase(); // Convert the word to lowercase for case-insensitive comparison
                    let wordScore = {word_score}; // Initialize wordScore with the length of the word
                    //initialize wordScore in sessionStorate = -1 as alabel of not yet done
                    //sessionStorage.setItem('wordScore', -1);
                    local_tid = "{tid}";
                    let timer = null;
                    let alarmPlayed = false; // To prevent multiple sound overlaps
                    let cheerPlayed = false; // To play cheerful sound only once

                    function checkText() {{
                        // Get the value from the input field and convert it to lowercase for case-insensitive comparison
                        var inputText = document.getElementById("textInput").value.toLowerCase();
                        var updatedText = "";
                        var lastIndex = 0;
                        var allMatch = true;

                        // Iterate over each character in the word
                        for (let i = 0; i < word.length; i++) {{
                            if (i < inputText.length) {{
                                if (inputText[i] === word[i] && allMatch) {{
                                    // Matching character, keep it green
                                    updatedText += '<span style="color: green;">' + inputText[i] + '</span>';
                                    lastIndex = i + 1;
                                    alarmPlayed = false; // Reset alarm
                                }} else {{
                                    // Non-matching character, make it red, stop further matching, and play the alarm sound
                                    updatedText += '<span style="color: red;">' + inputText[i] + '</span>';
                                    if (!alarmPlayed) {{
                                        document.getElementById("alarmSound").play(); // Play the alarm sound
                                        alarmPlayed = true; // Prevent multiple plays
                                        if (wordScore > 0) {{
                                            wordScore--; // Deduct one point for the wrong character if score is above zero
                                        }}
                                    }}
                                    allMatch = false;
                                }}
                            }} else {{
                                // Display underscores for spaces and dashes for other characters
                                updatedText += word[i] === ' ' ? '_' : '-'; 
                            }}
                        }}

                        // Update the score display
                        document.getElementById("scoreArea").innerHTML = "Score: " + wordScore;
                        
                        // Display the formatted text
                        document.getElementById("displayArea").innerHTML = updatedText;

                        // Check if the entire input matches the word
                        if (inputText === word && !cheerPlayed) {{
                            document.getElementById("cheerfulSound").play();
                            cheerPlayed = true; // Play cheerful sound only once

                            // Disable the input field since the input matches the word
                            document.getElementById("textInput").disabled = true;

                            //navigator.clipboard.writeText(wordScore)
                            sessionStorage.setItem('wordScore', wordScore);
                            
                            
                            // Print the wordScore to the console for debugging
                            console.log('wordScore:', wordScore);
                            console.log("wordScore from sessionStorage:", sessionStorage.getItem('wordScore'));
                        }}

                        // Clear the previous timer if it exists
                        if (timer) {{
                            clearTimeout(timer);
                        }}

                        // Set a new timer to remove the red characters after 0.5 seconds
                        timer = setTimeout(function() {{
                            // Only keep the matching part of the input text
                            document.getElementById("textInput").value = document.getElementById("textInput").value.substring(0, lastIndex);

                            // Move the cursor to the end of the input
                            document.getElementById("textInput").focus();
                            document.getElementById("textInput").setSelectionRange(lastIndex, lastIndex);
                        }}, 500);
                    }}
                </script>
            </body>
        </html>
        """,
        height=130  # Adjust height as needed
    )   


def show_result(current_row_data):
    tab1, tab2 = st.tabs(["Image", "Result"])
    with tab1:
        # Check if the image URL is valid; if not, use the placeholder image
        image_url = current_row_data["Image"].iloc[0]
        col1,col2 = st.columns([1,4])
        with col1:
            st.write(" ")
        with col2:
            st.image(fetch_and_resize_image(image_url if image_url else PLACEHOLDER_IMAGE, IMAGE_SIZE))
            #t = streamlit_js_eval(js_expressions="sessionStorage.getItem('wordScore');", key = "Get_Score2")         
    with tab2:  
        st.write(" ")
        st.subheader(f"{current_row_data['Word'].iloc[0]}")
        word_phone = ""
        if pd.notna(current_row_data['WordPhonetic'].iloc[0]):
            word_phone = current_row_data['WordPhonetic'].iloc[0]
        st.write(f" {word_phone}")

def gen_audio(word, lang_code):
    # tts = gTTS(text = word, lang = lang_code) # Generate speech
    # with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp: # Save the speech to a temporary file
    #     tts.save(fp.name)
    # return fp.name
    tts = gTTS(text=word, lang=lang_code)
    audio_fp = io.BytesIO()  # Create an in-memory byte stream
    tts.write_to_fp(audio_fp)  # Write audio to the stream
    audio_fp.seek(0)  # Move the pointer to the start of the stream

    # Encode audio data to base64
    audio_bytes = audio_fp.read()
    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    return audio_b64

def update_test_result_df(df, word_index, score):
    if score >= 0:
        df.loc[df['order'] == word_index, ['Score', 'Complete']] = [score, 'Y']
    else:
        df.loc[df['order'] == word_index, ['Score', 'Complete']] = [-1, 'N']
    return df

# Define a function to display data of the current row
def display_current_row(df, order_number):
    num_of_problems = len(df)
    current_row_data = df[df['order']== order_number]  
    current_word = current_row_data['Word'].iloc[0]
    current_langcode = current_row_data['LanguageCode'].iloc[0]
    st.session_state.word_audio = gen_audio(current_word, current_langcode)
    
    st.write(f"Problem {order_number}/{num_of_problems}")
    col1, col2 = st.columns([1,2])
    with col1:
        with st.container(border=1):
            show_result(current_row_data)
            #Display a button for trigger Audio play
            if st.button("Play Audio"):
                # Custom CSS to resize the audio player
                st.markdown(
                    """
                    <style>
                    audio {
                        width: 100%;
                        max-height: 40px;
                        /*max-width: 300px;  Adjust the max-width as needed */
                        margin: 0 auto; /*Center the audio player */
                        display: block;
                    }
                    </style>
                    """, 
                    unsafe_allow_html=True
                )
                # Create the HTML5 audio player using base64-encoded audio from session state
                audio_html = f"""
                    <audio controls autoplay>
                    <source src="data:audio/mp3;base64,{st.session_state.word_audio}" type="audio/mp3">
                    Your browser does not support the audio element.
                    </audio>
                    """
                # Display the HTML5 audio player
                st.markdown(audio_html, unsafe_allow_html=True)
              
    with col2:
        container_style = """
            <div style='
            width:100%;
            overflow:auto;
            font-size:2.5em;
            display: flex; 
            align-items: center; 
            justify-content: center; 
            border: 1px solid lightgray; 
            border-radius: 8px;  /* Rounded corners */
            background-color:#D9EEE1; 
            '>
                <b>{}</b>
            </div>
            """
        # Use st.markdown to render the HTML content
        st.markdown(container_style.format(
            current_row_data['Description'].iloc[0]
            ), unsafe_allow_html=True)
        word_matching(current_row_data['Word'].iloc[0], st.session_state.tid)  
        temp = streamlit_js_eval(js_expressions="sessionStorage.getItem('wordScore');", key = "Get_Score3")
    if temp != -1 and temp is not None:
        st.session_state.last_score = float(temp)
        st.session_state.test_result = update_test_result_df(st.session_state.test_result, st.session_state.word_index-1, st.session_state.last_score)
    streamlit_js_eval(js_expressions="sessionStorage.setItem('wordScore', -1);", key="clear1")
    
    incol1, incol2 = st.columns([3,1])
    with incol1:    
        st.write(" ")
    with incol2:
        # Determine the label and action based on the current index
        if st.session_state.word_index < num_of_problems:
            button_label = "Next"  
        else:
            button_label = "Submit"
        if st.button(button_label, key="next_word"):
            if st.session_state.word_index < num_of_problems:
                st.session_state.word_index += 1
                st.session_state.last_score = None
                st.rerun()
            if st.session_state.word_index == num_of_problems:
                st.session_state.page = "result_page"
                st.rerun()
            
                        

def init_test_result_df(df_test_words):
    df = pd.DataFrame({
        'order': df_test_words['order'],
        'WordID': df_test_words['WordID'],
        'Word': df_test_words['Word'],
        'Description': df_test_words['Description'],
        'MaxScore': df_test_words['Word'].apply(lambda x: len(x.replace(" ", ""))),
        'Score': -1,
        'Complete': 'N'
    })
    return df

def main_do_test():
    # Handle paging displaying session
    if st.session_state.page == 'do_test':
        selected_test = st.session_state.get("selected_test")
        if not selected_test:
            st.write("No TestID selected.")
            return
    else: 
        st.session_state.page == 'test_list'
        return
    
    # Initialize the word_index if not exist
    if 'word_index' not in st.session_state:
        st.session_state.word_index = 1 
    
    test_id = int(selected_test)
    # Get the filtered words data base on TestID (selected_test) from WordsList.csv
    df_test_words = get_filtered_words(test_id)
    df_test_words = set_words_order(df_test_words, order_type = "sequence") # order_type = "sequence"|"random"
        
    # Initialize the test_result dataframe if not exist
    if 'test_result' not in st.session_state or st.session_state.test_result is None:
        st.session_state.test_result = init_test_result_df(df_test_words)
        
    st.subheader(f"Do Test - {test_id}")
    display_current_row(df_test_words,st.session_state.word_index)

main_do_test()