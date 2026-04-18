# ============================================================================
# IMPORTS
# ============================================================================
import streamlit as st
import pandas as pd
from streamlit_js_eval import streamlit_js_eval


# ============================================================================
# DATA HANDLING
# ============================================================================

def update_test_result_df(df, word_index, score):
    """Update test result dataframe with score for a specific word."""
    idx = df.index[word_index - 1]
    df.loc[idx, ['Score', 'Complete']] = [score, 'Y'] if score >= 0 else [-1, 'N']
    return df


def capture_final_score():
    """Capture the final score from browser session storage."""
    temp = streamlit_js_eval(
        js_expressions="sessionStorage.getItem('wordScore');", 
        key="Final_Capture"
    )
    return temp


def reset_browser_storage():
    """Reset browser session storage for the next test run."""
    streamlit_js_eval(
        js_expressions="sessionStorage.setItem('wordScore', -1);", 
        key="final_reset"
    )


# ============================================================================
# STYLING FUNCTIONS
# ============================================================================

def style_rows(row):
    """Apply row-based styling based on test result completion and score."""
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


def bold_words(val):
    """Apply bold text styling to Word column."""
    return 'font-weight: bold' if val else ''


# ============================================================================
# UI & DISPLAY FUNCTIONS
# ============================================================================

def display_summary_stats(result_df):
    """Display test summary statistics: correct answers, points, and percentage."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("Correct:")
        correct_count = len(result_df[result_df['Score'] == result_df['MaxScore']])
        st.subheader(f"{correct_count}/{len(result_df)}")
    
    with col2:
        st.write("Points:")
        total_points = result_df['Score'].sum()
        max_points = result_df['MaxScore'].sum()
        st.subheader(f"{total_points}/{max_points}")
    
    with col3:
        st.write("Percent:")
        percentage = round(result_df['Score'].sum() / result_df['MaxScore'].sum() * 100, 2)
        st.subheader(f"{percentage}%")


def display_results_table(result_df):
    """Display styled results table with color-coded performance."""
    result_df['WordID'] = result_df['WordID'].astype(int)
    styled_df = result_df.style.apply(style_rows, axis=1)\
        .applymap(bold_words, subset=['Word'])
    st.dataframe(styled_df)


def display_back_button():
    """Display back button and handle navigation to test list."""
    if st.button("🔙 Back", key='result_page_back'):
        st.session_state.page = 'test_list'
        st.session_state.word_index = 1
        st.session_state.selected_test = None
        st.session_state.test_result = None
        st.session_state.AttemptID = None
        st.rerun()


# ============================================================================
# MAIN LOGIC
# ============================================================================

def main_result_page():
    """Main function to orchestrate the result page workflow."""
    # Capture and update the final score from browser storage
    final_score = capture_final_score()
    
    if final_score is not None and int(final_score) != -1:
        st.session_state.test_result = update_test_result_df(
            st.session_state.test_result, 
            st.session_state.word_index, 
            float(final_score)
        )
    
    # Reset browser storage for the next possible test run
    reset_browser_storage()

    if st.session_state.page == 'result_page':
        # Get test results
        result_df = st.session_state.get('test_result')
        
        # Display summary statistics
        display_summary_stats(result_df)
        
        # Display results table
        display_results_table(result_df)
        
        # Display back button
        display_back_button()
    else: 
        st.session_state.page == 'test_list'
        return


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main_result_page()