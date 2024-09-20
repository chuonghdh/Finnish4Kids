import streamlit as st
import pandas as pd
import os
import requests
import common as cm
from io import BytesIO
from PIL import ImageOps, Image
from Manage_Test import upload_test as up

from Manage_Test.edit_question import show_question_editor

# Constants
#TESTS_CSV_FILE_PATH = 'Data/TestsList.csv'
PLACEHOLDER_IMAGE = "Data/image/placeholder_image.png"
IMAGE_SIZE = 60

# Image-related Functions
@st.cache_data
def fetch_image(link):
    """Fetch image from the provided URL."""
    try:
        if not pd.isna(link) and link.strip():
            response = requests.get(link)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
    except Exception:
        pass  # Silent fail on error
    return None

def resize_and_crop_image(image, size):
    """Resize and crop the image to a square."""
    try:
        return ImageOps.fit(image, (size, size), Image.LANCZOS)
    except Exception:
        return None

def display_image_or_text(link, column, size=IMAGE_SIZE):
    """Display image or placeholder if the link is invalid."""
    image = fetch_image(link)
    
    if image:
        image = resize_and_crop_image(image, size)
        if image:
            column.image(image, width=size)
    if not image:  # If fetching image failed, show the placeholder
        try:
            placeholder = Image.open(PLACEHOLDER_IMAGE)
            placeholder = resize_and_crop_image(placeholder, size)
            if placeholder:
                column.image(placeholder, width=size)
        except Exception as e:
            st.error(f"Error displaying placeholder image: {e}")

# UI Functions
def show_data_table():
    """Display the data table with rename, delete, and edit question options."""
    df = cm.read_csv_file(cm.TESTS_CSV_FILE_PATH, cm.prd_TestsList_path)
    if df.empty:
        st.write("No tests available.")
        return
 
    # Display the table header
    st.write(
        """
        <div class='table-header'>
            <span style="flex: 0.3;">ID</span>
            <span style="flex: 1;">Name</span>
            <span style="flex: 1;">Description</span>
            <span style="flex: 0.3;">Lang</span>
            <span style="flex: 0.5;">Image</span>
            <span style="flex: 0.5;">Created By</span>
            <span style="flex: 0.5;">Updated By</span>
            <span style="flex: 0.45;"></span>
            <span style="flex: 0.45;"></span>
            <span style="flex: 0.6;"></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if 'rename_mode' not in st.session_state:
        st.session_state.rename_mode = None  # Track the index of the row in rename mode

    for i, row in df.iterrows():
        display_table_row(i, row, df)
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button('➕ Add Test'):
            st.session_state.page = 'form'
            st.rerun()
    with col2:
        if st.button('⬆️ Upload Test'):
            st.warning("Upload Test Function!!!")
            st.session_state.page = 'upload_page'
            st.rerun()

def display_table_row(row_index, row, df):
    """Display a single row in the data table."""
    num_columns = len(row) + 3  # Additional column for the 'Edit Questions' button
    cols = st.columns([0.3, 1, 1, 0.2, 0.5, 0.5, 0.5, 0.45, 0.45, 0.6][:num_columns])

    # Wrap the row in a div with the class 'table-row' for styling
    with st.container():
        st.write('<div class="table-row">', unsafe_allow_html=True)
        
        if st.session_state.rename_mode == row_index:
            handle_rename_mode(row_index, row, cols)
        else:
            handle_normal_mode(row_index, row, cols)

        st.write('</div>', unsafe_allow_html=True)

def handle_rename_mode(row_index, row, cols):
    """Handle the rename mode for a row, allowing only certain fields to be edited."""
    new_data = []
    for j, (col_name, col_value) in enumerate(row.items()):
        if col_name in ['TestName', 'TestDescription', 'Image']:
            new_data.append(cols[j].text_input(f' ', label_visibility='collapsed' ,value=col_value, key=f'{col_name}_{row_index}'))
        else:
            new_data.append(col_value)
            if col_name == 'TestID':
                cols[j].write(int(col_value))
            else:    
                cols[j].write(col_value)

    done_button = cols[len(row)].button('✅', help="Done", key=f'done_{row_index}')
    if done_button:
        st.session_state.rename_mode = None
        cm.update_to_csv(row_index = row_index, new_data = new_data, repo_path = cm.TESTS_CSV_FILE_PATH, prd_path = cm.prd_TestsList_path)
        st.rerun()

def handle_normal_mode(row_index, row, cols):
    """Handle the normal mode for a row."""
    for j, (col_name, col_value) in enumerate(row.items()):
        if col_name == 'Image':
            display_image_or_text(col_value, cols[j])
        else:
            if col_name == 'TestID':
                col_value_int = int(col_value)  # Convert col_value to an integer and then display it
                cols[j].markdown(f"<p style='font-size:16px; font-weight:bold;'>{col_value_int}</p>", unsafe_allow_html=True)
            elif col_name in ['TestDescription', 'Language', 'CreatedBy', 'LastUpdatedBy']:
                cols[j].markdown(f"<p style='font-size:12px;'>{col_value}</p>", unsafe_allow_html=True)
            elif col_name == 'TestName':
                cols[j].markdown(f"<p style='font-size:16px; font-weight:bold;'>{col_value}</p>", unsafe_allow_html=True)
            else:
                cols[j].write(col_value)

    edit_questions_button = cols[len(row)].button(
        label="📝", 
        help="Edit Questions",
        key=f'edit_questions_{row_index}'
    )
    rename_button = cols[len(row) + 1].button(
        label="✏️", 
        help="Rename",
        key=f'rename_{row_index}'
    )
    delete_button = cols[len(row) + 2].button(
        label="🗑️", 
        help="Delete",
        key=f'delete_{row_index}'
    )
    
    if edit_questions_button:
        st.session_state.selected_test = row['TestID']
        st.session_state.page = 'edit_question'
        st.rerun()

    if rename_button:
        st.session_state.rename_mode = row_index
        st.rerun()

    if delete_button:
        cm.delete_from_csv(row_index=row_index, repo_path=cm.TESTS_CSV_FILE_PATH, prd_path=cm.prd_TestsList_path)
        st.rerun() 

def add_test_form():
    """Create and handle the add test form."""
    st.write("### Add New Test")
    form = st.form(key='add_entry_form')

    df = cm.read_csv_file(cm.TESTS_CSV_FILE_PATH, cm.prd_TestsList_path)

    if df.empty:
        new_test_id = 1  # Start TestID from 1 if the dataframe is empty
    else:
        df['TestID'] = pd.to_numeric(df['TestID'], errors='coerce')
        new_test_id = df['TestID'].max() + 1

    form.text_input('TestID', value=str(new_test_id), disabled=True, key='TestID')

    form_data = {col: form.text_input(f'Enter the {col}:') for col in df.columns if col != 'TestID'}

    submit, cancel = form.columns(2)
    if submit.form_submit_button(label='Add New Test'):
        form_data['TestID'] = str(new_test_id)
        new_entry = {col: [form_data[col]] for col in df.columns}
        cm.save_to_csv(data=new_entry, repo_path=cm.TESTS_CSV_FILE_PATH ,prd_path=cm.prd_TestsList_path)
        st.session_state.page = 'table'
        st.rerun()

    if cancel.form_submit_button(label='Cancel'):
        st.session_state.page = 'table'
        st.rerun()

def edit_questions_page():
    """Display the edit questions page for the selected test."""
    test_id = st.session_state.selected_test
    st.write(f"### Edit Questions for Test ID: {test_id}")

    if st.button("🔙 Back to Main Page"):
        st.session_state.page = 'table'
        st.rerun()

def show_page_testlist():
    """Page routing logic."""
    if st.session_state.page == 'table':
        show_data_table()
    elif st.session_state.page == 'form':
        add_test_form()
    elif st.session_state.page == 'edit_question':
        #edit_questions_page()
        show_question_editor()
    elif st.session_state.page == 'upload_page':
        up.show_upload_page()

# Main Page of Edit Test
# Main Page Title
st.title("Edit Your Tests")  

if 'page' not in st.session_state:
    st.session_state.page = 'table'
if 'selected_test' not in st.session_state:
    st.session_state.selected_test = None

show_page_testlist()

