# app.py

import streamlit as st
import awswrangler as wr
import time
import boto3
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from openai_utils import process_symptom_class, init_messages
from ui import get_input_symptom_class, display_symptom_class_results, display_remedies, display_final_analysis, adjust_symptom_class
import pandas as pd
from helpers import (
    initialize_openai,
    search_top_similar_symptoms,
)


# Initialize a session using Streamlit secrets
session = boto3.Session(
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
    region_name=st.secrets["AWS_DEFAULT_REGION"]
)

# Create an S3 client
s3 = session.client('s3')

# Initialize OpenAI client
client = initialize_openai()

# Load data
@st.cache_data
def load_data():
    symptom_data = wr.s3.read_parquet("s3://project-z-mambo/symptoms/relevant_symptoms.gz")
    return symptom_data

@st.cache_data
def download_s3_file(bucket_name, s3_key, local_filename):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, s3_key, local_filename)



bucket_name = 'project-z-mambo'
s3_key = 'symptoms/synthesis.db'
local_filename = 'synthesis.db'

download_s3_file(bucket_name, s3_key, local_filename)

data = load_data()


# Define a callback function to update the session state
def proceed_to_mittelsuche():
    st.session_state.current_step = 'mittelsuche'
    st.rerun()
    


# Initialize session state
def initialize_session():
    if 'conversation' not in st.session_state:
        st.session_state.conversation = init_messages()
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'input_symptom_class'
    if 'user_input_symptom_class' not in st.session_state:
        st.session_state.user_input_symptom_class = ''
    if 'oberkategorie' not in st.session_state:
        st.session_state.oberkategorie = ''  # New output variable
    if 'unterkategorie' not in st.session_state:
        st.session_state.unterkategorie = ''  # New output variable
    if 'suchpfad' not in st.session_state:
        st.session_state.suchpfad = ''
    if 'begründung' not in st.session_state:
        st.session_state.begründung = ''  # New output variable
    # Initialize top_results in session state if it doesn't exist
    if "top_results" not in st.session_state:
        st.session_state.top_results = pd.DataFrame()  # Empty DataFrame structure
    if 'final_results' not in st.session_state:
        st.session_state.final_results = []  # Initialize as an empty list to store remedies

initialize_session()
# st.write("After click Current session state:", st.session_state)


# Define the new processing function within app.py
def process_symptom_class_state():
    """
    Processes the symptom class input by calling the OpenAI function and stores the results.
    """
    user_input = st.session_state.get('user_input_symptom_class', '')
    conversation = st.session_state.conversation  # Pass the full conversation
    try:
        with st.spinner('Verarbeite Symptomklasse...'):
            oberkategorie, unterkategorie, suchpfad, begründung, assisstant_response = process_symptom_class(user_input, conversation)
            # Store the outputs in session state
            st.session_state.oberkategorie = oberkategorie
            st.session_state.unterkategorie = unterkategorie
            st.session_state.suchpfad = suchpfad
            st.session_state.begründung = begründung
            # Append the assistant response to the conversation
            st.session_state.conversation = st.session_state.conversation +  [{ "role": "assistant", "content": [ { "text": assisstant_response, "type": "text" }] }]
    except Exception as e:
        st.error(f"Fehler bei der Verarbeitung der Symptomklasse: {e}")
        st.stop()

    # Transition to the new state
    st.session_state.current_step = 'display_symptom_class_results'
    st.rerun()



# Step 4: Perform similarity search
def perform_similarity_search():
    st.write("**Bestätigte Anfrage: Suche nach Treffer für Suchpfad**")
    st.write(st.session_state.suchpfad)

    # Perform the search only if top_results is empty or newly initialized
    if st.session_state.top_results.empty:
        try:
            with st.spinner('Ähnliche Symptome werden gesucht...'):
                st.session_state.top_results = search_top_similar_symptoms(
                    st.session_state.suchpfad, data, st.session_state.oberkategorie,st.session_state.unterkategorie ,top_n=100
                )
        except Exception as e:
            st.error(f"Fehler bei der Suche nach ähnlichen Symptomen: {e}")
            st.stop()

    # Display results using st_aggrid
    if not st.session_state.top_results.empty:
        st.write("**Top ähnliche Symptome:**")
    
        # Configure grid options
        gb = GridOptionsBuilder.from_dataframe(st.session_state.top_results[['id', 'category', 'path', 'similarity']])
        gb.configure_pagination(paginationAutoPageSize=True)  # Enable pagination
        gb.configure_default_column(editable=False, groupable=True, filter=True)
        gb.configure_selection(selection_mode="multiple", use_checkbox=True)  # Enable single row selection
        grid_options = gb.build()
    
        # Display the grid
        grid_response = AgGrid(
            st.session_state.top_results[['id', 'category', 'path', 'similarity']],
            gridOptions=grid_options,
            height=400,
            fit_columns_on_grid_load=True,
            update_mode=GridUpdateMode.SELECTION_CHANGED,  # Update on selection change
        )

        # Initialize top_results in session state if it doesn't exist
        if "selected_rows" not in st.session_state:
            st.session_state.selected_rows = pd.DataFrame(columns=['id', 'category', 'path', 'similarity'])  # Empty DataFrame
        # Retrieve selected rows
        st.session_state.selected_rows = grid_response['selected_rows']

        # # Debugging: Print the type and content of selected_rows
        # st.write("Type of selected_rows:", type(selected_rows))
        # st.write("Content of selected_rows:", selected_rows)

        # Check if selected_rows is not empty
        if st.session_state.selected_rows is not None and not st.session_state.selected_rows.empty:
            st.write("**Sie haben folgende Symptome ausgewählt:**")
            for i, row in st.session_state.selected_rows.reset_index().iterrows():
                st.write(f"***Symptom_{i+1}***: { row['category']} - {row['path']}")

            # Display "Mittel finden" button to proceed to the next stage
            st.button("Mittel finden", on_click= proceed_to_mittelsuche)
                
        else:
            st.write("Keine Symptome ausgewählt.")


# Main controller function
def run_app():
    if st.session_state.current_step == 'input_symptom_class':
        get_input_symptom_class()
    elif st.session_state.current_step == 'processing_symptom_class':
        process_symptom_class_state()
    elif st.session_state.current_step == 'display_symptom_class_results':
        display_symptom_class_results()
    elif st.session_state.current_step == 'adjustment':
        adjust_symptom_class()
    elif st.session_state.current_step == 'search':
        perform_similarity_search()
    elif st.session_state.current_step == 'mittelsuche':
        display_remedies()
    elif st.session_state.current_step == 'final_analysis':
        display_final_analysis()


# Run the app
run_app()
