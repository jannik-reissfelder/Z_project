import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from helpers import get_remedies
import pandas as pd

def get_input_symptom_class():
    st.title("Symptom-Klassen Analyse")
    user_input = st.text_area(
        "Bitte geben Sie die Symptomklasse des Patienten ein:",
        placeholder="*Beispiel*: Schlafstörungen nach Mitternacht"
    )

    if st.button("Symptomklasse verarbeiten"):
        if user_input:
            st.session_state.current_step = 'processing_symptom_class'
            st.session_state.user_input_symptom_class = user_input
            st.rerun()
        else:
            st.warning("Bitte geben Sie die Symptomklasse des Patienten ein.")



def display_symptom_class_results():
    """
    Displays the results from the symptom class processing and provides a button to proceed.
    """
    st.header("Ergebnisse der Symptomklassenanalyse")

    # Retrieve the outputs from session state
    oberkategorie = st.session_state.get('oberkategorie', 'Nicht verfügbar')
    unterkategorie = st.session_state.get('unterkategorie', 'Nicht verfügbar')
    begründung = st.session_state.get('begründung', 'Nicht verfügbar')

    # Display the results
    st.subheader("Eingabe-Symptom")
    st.write(st.session_state.user_input_symptom_class)

    st.subheader("Oberkategorie")
    st.write(oberkategorie)

    st.subheader("Unterkategorie")
    st.write(unterkategorie)

    st.subheader("Begründung")
    st.write(begründung)

    # Button to proceed to the next step
    if st.button("Weiter mit Symptom-Suche"):
        st.session_state.current_step = 'enrich_query'
        st.rerun()


def display_remedies():
    """
    Displays selected symptoms and provides a button to fetch remedies for each symptom.
    """
    st.write("**Selected Symptoms:**")

    # Retrieve selected rows
    selected_rows = st.session_state.selected_rows

    if selected_rows is not None and not selected_rows.empty:
        for i, row in selected_rows.iterrows():
            symptom_id = row['id']
            symptom_text = row['Relevantes Symptom']

            # Display each symptom with a "Show Remedies" button
            with st.expander(f"Symptom ID: {symptom_id} - {symptom_text}", expanded=False):
                if st.button(f"Show Remedies for Symptom ID {symptom_id}", key=f"remedy_{symptom_id}"):
                    # Fetch remedies for the current symptom_id
                    remedies = get_remedies(symptom_id)

                    if remedies:
                        st.write("**Remedies:**")
                        # Option 2: Display as a table (uncomment if preferred)
                        remedies_df = pd.DataFrame(remedies)
                        remedies_df.rename(columns={
                            'abbreviation': 'Kürzel',
                            'description': 'Mittel',
                            'degree': 'Wertigkeit'
                        }, inplace=True)
                        # sort by degree
                        remedies_df = remedies_df.sort_values(by='Wertigkeit', ascending=False)
                        st.table(remedies_df)
                    else:
                        st.write("No remedies found for this symptom.")
    else:
        st.write("No symptoms selected.")
