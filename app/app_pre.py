# app.py

import streamlit as st
import time
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

import pandas as pd
from helpers import (
    initialize_openai,
    search_top_similar_symptoms,
    enrich_query, get_remedies
)

# Initialize OpenAI client
client = initialize_openai()

# Load data
@st.cache_data
def load_data():
    return pd.read_parquet("trial_sym_rem_embeddings.gz")

data = load_data()

# Define a callback function to update the session state
def proceed_to_mittelsuche():
    st.session_state.current_step = 'mittelsuche'
    st.rerun()
    

# Define system message for the assistant
system_message = "Du bist deutscher Homöopath und analysierst die Symptome des Patienten nach dem Buch des Synthesis."

# Initialize session state
def initialize_session():
    if 'conversation' not in st.session_state:
        st.session_state.conversation = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": "Extrahiere die Symptome des Patienten und paraphrasiere die Symptomatik falls zutreffend nach dem deutschen Synthesis Buch der Homöopathen. Bitte die Schlüssel-Symptome nach Synthesis extrahieren, gerne Komma separiert. Bitte NUR die Symptomatik geben, kurz und präzise."},
            {"role": "user", "content": "Bitte antworte als würdest du versuchen so präzise wie möglich den Suchpfad im Synthesis zu finden, auf Basis der Symptomatik."}
        ]
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'input'
    if 'enriched_query' not in st.session_state:
        st.session_state.enriched_query = None

initialize_session()


st.write("After click Current session state:", st.session_state)

# Step 1: Get user input
def get_user_input():
    st.title("Symptom-Suche nach Synthesis")
    user_input = st.text_area("Bitte geben Sie das Symptom des Patienten ein:", placeholder="*Beispiel*: Der Patient schläft unruhig nach Mitternacht")
    
    if st.button("Symptom analysieren"):
        if user_input:
            st.session_state.conversation.append({"role": "user", "content": f"User Input: {user_input}"})
            st.session_state.current_step = 'enrich_query'
            st.rerun()
        else:
            st.warning("Bitte geben Sie die Symptome des Patienten ein.")

# Step 2: Generate enriched query
def generate_enriched_query():
    try:
        with st.spinner('Enriching query...'):
            enriched_query = enrich_query(client, st.session_state.conversation)
    except Exception as e:
        st.error(f"Fehler beim Generieren des erweiterten Abfrage: {e}")
        st.stop()

    st.session_state.conversation.append({"role": "assistant", "content": enriched_query})
    st.session_state.enriched_query = enriched_query
    st.session_state.current_step = 'adjustment'
    st.rerun()

def adjust_enriched_query():
    st.write("**Enriched Query Vorschlag:**")
    st.write(st.session_state.enriched_query)

    # Option to adjust or finalize the enriched query
    adjust = st.radio(
        "Möchten Sie das vorgeschlagene Symptomset anpassen?",
        ("Nein", "Ja"),
        index=1 if st.session_state.get("adjust_choice", "Ja") == "Ja" else 0,
        key="adjust_radio"
    )

    if adjust == "Ja":
        # User opts to adjust the enriched query
        adjustment = st.text_input(
            "Bitte geben Sie die gewünschten Anpassungen ein:",
            key="adjust_input"
        )

        if st.button("Anpassungen übernehmen", key="apply_adjustment"):
            if adjustment:
                st.session_state.conversation.append({"role": "user", "content": f"Anpassung: {adjustment}"})
                
                try:
                    with st.spinner('Anpassungen werden verarbeitet...'):
                        enriched_query = enrich_query(client, st.session_state.conversation)
                except Exception as e:
                    st.error(f"Fehler beim Generieren des angepassten erweiterten Abfrage: {e}")
                    st.stop()

                st.session_state.conversation.append({"role": "assistant", "content": enriched_query})
                st.session_state.enriched_query = enriched_query
                st.session_state.current_step = 'adjustment'  # Stay in adjustment loop
                st.rerun()
            else:
                st.warning("Bitte geben Sie die gewünschten Anpassungen ein.")

    else:
        # User opts to finalize and proceed to search
        st.write("**Bestätigte Anfrage:**")
        st.write(st.session_state.enriched_query)
        st.session_state.current_step = 'search'
        st.rerun()

# Step 4: Perform similarity search
def perform_similarity_search():
    st.write("**Bestätigte Anfrage:**")
    st.write(st.session_state.enriched_query)

    # Initialize top_results in session state if it doesn't exist
    if "top_results" not in st.session_state:
        st.session_state.top_results = pd.DataFrame(columns=['symptom_id', 'relevant_text'])  # Empty DataFrame structure

    # Perform the search only if top_results is empty or newly initialized
    if st.session_state.top_results.empty:
        if st.button("Ähnliche Symptome suchen"):
            try:
                with st.spinner('Ähnliche Symptome werden gesucht...'):
                    st.session_state.top_results = search_top_similar_symptoms(
                        st.session_state.enriched_query, data, top_n=100
                    )
            except Exception as e:
                st.error(f"Fehler bei der Suche nach ähnlichen Symptomen: {e}")
                st.stop()

    # Display results using st_aggrid
    if not st.session_state.top_results.empty:
        st.write("**Top ähnliche Symptome:**")
    
        # Configure grid options
        gb = GridOptionsBuilder.from_dataframe(st.session_state.top_results[['symptom_id', 'relevant_text', 'similarity']])
        gb.configure_pagination(paginationAutoPageSize=True)  # Enable pagination
        gb.configure_default_column(editable=False, groupable=True, filter=True)
        gb.configure_selection(selection_mode="multiple", use_checkbox=True)  # Enable single row selection
        grid_options = gb.build()
    
        # Display the grid
        grid_response = AgGrid(
            st.session_state.top_results[['symptom_id', 'relevant_text', 'similarity']],
            gridOptions=grid_options,
            height=400,
            fit_columns_on_grid_load=True,
            update_mode=GridUpdateMode.SELECTION_CHANGED,  # Update on selection change
        )

        # Initialize top_results in session state if it doesn't exist
        if "selected_rows" not in st.session_state:
            st.session_state.selected_rows = pd.DataFrame(columns=['symptom_id', 'relevant_text',  'similarity'])  # Empty DataFrame
        # Retrieve selected rows
        st.session_state.selected_rows = grid_response['selected_rows']

        # # Debugging: Print the type and content of selected_rows
        # st.write("Type of selected_rows:", type(selected_rows))
        # st.write("Content of selected_rows:", selected_rows)

        # Check if selected_rows is not empty
        if st.session_state.selected_rows is not None and not st.session_state.selected_rows.empty:
            st.write("**Sie haben folgende Symptome ausgewählt:**")
            for i, row in st.session_state.selected_rows.iterrows():
                st.write(f"Symptom ID: {row['symptom_id']}, Text: {row['relevant_text']}")

            # Display "Mittel finden" button to proceed to the next stage
            st.button("Mittel finden", on_click= proceed_to_mittelsuche)
                
        else:
            st.write("Keine Symptome ausgewählt.")



    # Reset for a new analysis
    if st.button("Neue Analyse starten"):
        st.write("Starting new session...")
        time.sleep(1)
        reset_session_state()  # This sets current_step to 'input' explicitly
        
           
def display_remedies():
    """
    Displays selected symptoms and provides a button to fetch remedies for each symptom.
    """
    st.write("**Selected Symptoms:**")

    # Retrieve selected rows
    selected_rows = st.session_state.selected_rows

    if selected_rows is not None and not selected_rows.empty:
        for i, row in selected_rows.iterrows():
            symptom_id = row['symptom_id']
            symptom_text = row['relevant_text']
            
            # Display each symptom with a "Show Remedies" button
            with st.expander(f"Symptom ID: {symptom_id} - {symptom_text}", expanded=False):
                if st.button(f"Show Remedies for Symptom ID {symptom_id}", key=f"remedy_{symptom_id}"):
                    # Fetch remedies for the current symptom_id
                    remedies = get_remedies(symptom_id)
                    
                    if remedies:
                        st.write("**Remedies:**")
                        for remedy in remedies:
                            st.write(f"- **{remedy['abbreviation']}**: {remedy['description']}")
                    else:
                        st.write("No remedies found for this symptom.")
    else:
        st.write("No symptoms selected.")        

            


# Helper to reset session state for a new analysis
def reset_session_state():
    st.session_state.current_step = 'input'
    st.session_state.conversation = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": "Extrahiere die Symptome des Patienten und paraphrasiere die Symptomatik falls zutreffend nach dem deutschen Synthesis Buch der Homöopathen. Bitte die Schlüssel-Symptome nach Synthesis extrahieren, gerne Komma separiert. Bitte NUR die Symptomatik geben, kurz und präzise."},
            {"role": "user", "content": "Bitte antworte als würdest du versuchen so präzise wie möglich den Suchpfad im Synthesis zu finden, auf Basis der Symptomatik."}
        ]
    st.session_state.enriched_query = None
    st.rerun()

# Main controller function
def run_app():
    if st.session_state.current_step == 'input':
        get_user_input()
    elif st.session_state.current_step == 'enrich_query':
        generate_enriched_query()
    elif st.session_state.current_step == 'adjustment':
        adjust_enriched_query()
    elif st.session_state.current_step == 'search':
        perform_similarity_search()
    elif st.session_state.current_step == 'mittelsuche':
        display_remedies()

# Run the app
run_app()
