import streamlit as st
import pandas as pd
import requests
from streamlit_js_eval import streamlit_js_eval

def update_test_result_df(df, word_index, score):
    if score >= 0:
        df.loc[df['order'] == word_index, ['Score', 'Complete']] = [score, 'Y']
    else:
        df.loc[df['order'] == word_index, ['Score', 'Complete']] = [-1, 'N']
    return df

# Function to apply row-based styling
def style_rows(row):
    if row['Complete'] == 'N':
        return ['background-color: lightgrey'] * len(row)
    elif row['Score'] == row['MaxScore']:
        return ['background-color: lightgreen'] * len(row)
    elif row['MaxScore'] - row['Score'] <= 2:
        return ['background-color: lightyellow'] * len(row)
    elif 2 < row['MaxScore'] - row['Score'] < 5:
        return ['background-color: yellow'] * len(row)
    elif row['MaxScore'] - row['Score'] >= 5:
        return ['background-color: red'] * len(row)
    return [''] * len(row)

# Function to apply bold text to 'Word' column
def bold_words(val):
    return 'font-weight: bold' if val else ''

def main_result_page():
    temp = streamlit_js_eval(js_expressions="sessionStorage.getItem('wordScore');", key = "Get_Score4")
    
    if temp != -1 and temp is not None: 
        st.session_state.last_score = float(temp)
        st.session_state.test_result = update_test_result_df(st.session_state.test_result, st.session_state.word_index, st.session_state.last_score)
    
    #streamlit_js_eval(js_expressions="sessionStorage.clear();", key="clear1")
    streamlit_js_eval(js_expressions="sessionStorage.setItem('wordScore', -1);", key="clear2")
    # Handle paging displaying session
    if st.session_state.page == 'result_page':
        # Show final result
        result_df = st.session_state.get('test_result')
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("Correct:")
            st.subheader(f"{len(result_df[result_df['Score'] == result_df['MaxScore']])}/{len(result_df)}")
        with col2:
            st.write("Points:")
            st.subheader(f"{result_df['Score'].sum()}/{result_df['MaxScore'].sum()}")
        with col3:
            st.write("Percent:")
            st.subheader(f"{round(result_df['Score'].sum()/result_df['MaxScore'].sum()*100, 2)}%")
        
        # Applying the style to the dataframe
        result_df['WordID'] = result_df['WordID'].astype(int)
        # Applying the styles to the dataframe
        styled_df = result_df.style.apply(style_rows, axis=1)\
            .applymap(bold_words, subset=['Word'])
        
        # Display the styled dataframe using st.dataframe
        st.dataframe(styled_df)
        #st.data_editor(result_df, disabled=True)
    else: 
        st.session_state.page == 'test_list'
        return
    
    # Clear the session storage using JavaScript
    #streamlit_js_eval("sessionStorage.clear();", key="clear")
    #streamlit_js_eval(js_expressions="sessionStorage.setItem('wordScore', -1);", key="Set_Score")
    if st.button("🔙 Back", key='result_page_back'):
        st.session_state.page = 'test_list'
        st.session_state.word_index = 1
        st.session_state.selected_test = None
        st.session_state.test_result = None
        st.session_state.AttemptID = None
        st.rerun()
    
main_result_page()