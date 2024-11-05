import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from helpers import get_remedies, partial_reset_session_state, full_reset_session_state, add_to_final_results
import pandas as pd

def get_input_symptom_class():
    st.title("Symptom Analyse")
    user_input = st.text_area(
        "Bitte beschreibe das Symptom des Patienten:",
        placeholder="*Beispiel*: Der Patient klagt über Schmerzen im rechten Knie."
    )

    if st.button("Symptom analysieren"):
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
    Displays selected symptoms and provides options to fetch remedies, add to results, or proceed to final analysis.
    """
    st.write("**Selected Symptoms:**")

    # Retrieve selected rows
    selected_rows = st.session_state.selected_rows

    if selected_rows is not None and not selected_rows.empty:
        for i, row in selected_rows.iterrows():
            symptom_id = row['id']
            symptom_text = row['Relevantes Symptom']

            # Initialize session state flags for each symptom
            show_remedies_key = f'show_remedies_{symptom_id}'
            remedies_key = f'remedies_{symptom_id}'

            if show_remedies_key not in st.session_state:
                st.session_state[show_remedies_key] = False

            # Create an expander for each symptom
            with st.expander(f"Symptom ID: {symptom_id} - {symptom_text}", expanded=False):
                # "Show Remedies" button
                if st.button(f"Show Remedies for Symptom ID {symptom_id}", key=f"remedy_{symptom_id}"):
                    # Fetch remedies for the current symptom_id
                    remedies = get_remedies(symptom_id)
                    # Store remedies and set flag to True
                    st.session_state[remedies_key] = remedies
                    st.session_state[show_remedies_key] = True

                # Check if remedies have been shown for this symptom
                if st.session_state[show_remedies_key]:
                    remedies = st.session_state.get(remedies_key, [])
                    if remedies:
                        st.write("**Remedies:**")
                        # Display remedies as a sorted table
                        remedies_df = pd.DataFrame(remedies)
                        remedies_df.rename(columns={
                            'abbreviation': 'Kürzel',
                            'description': 'Mittel',
                            'degree': 'Wertigkeit'
                        }, inplace=True)
                        # Sort by degree descending
                        remedies_df = remedies_df.sort_values(by='Wertigkeit', ascending=False)
                        st.table(remedies_df)

                        # "Add Remedies" button
                        if st.button(f"Add Remedies for Symptom ID {symptom_id} to Results", key=f"add_{symptom_id}"):
                            add_to_final_results(remedies, symptom_id)  # Call the helper function
                    else:
                        st.write("No remedies found for this symptom.")

        # Separator
        st.markdown("---")

        # Button to return to initial state
        if st.button("Zurück zur Symptom Suche"):
            partial_reset_session_state()

        # Button to proceed to final analysis
        if st.button("Weiter zu Finalem Analyse Ergebnis"):
            st.session_state.current_step = 'final_analysis'
            st.rerun()
    else:
        st.write("No symptoms selected.")

    # Display success message if remedies were added
    if st.session_state.get('added_message'):
        st.success(st.session_state['added_message'])
        del st.session_state['added_message']  # Clear the message after displaying





def display_final_analysis():
    """
    Displays the final accumulated remedies collected by the user throughout the session.
    Shows each remedy's total occurrence and summed degree, sorted by occurrence descending.
    Provides options to download the results or restart the session.
    """
    st.header("Finales Analyse Ergebnis")

    # Retrieve the final results from session state
    final_results = st.session_state.get('final_results', [])

    if final_results:
        # Convert the list of dictionaries to a DataFrame
        final_df = pd.DataFrame(final_results)

        # Aggregate remedies by abbreviation
        aggregated_df = final_df.groupby('abbreviation').agg(
            total_occurrence=pd.NamedAgg(column='abbreviation', aggfunc='count'),
            total_degree=pd.NamedAgg(column='degree', aggfunc='sum')
        ).reset_index()

        # Merge with descriptions to retain remedy descriptions
        descriptions = final_df[['abbreviation', 'description']].drop_duplicates()
        aggregated_df = pd.merge(aggregated_df, descriptions, on='abbreviation', how='left')

        # Rearrange columns for clarity
        aggregated_df = aggregated_df[['abbreviation', 'description', 'total_occurrence', 'total_degree']]

        #rename columns 'Kürzel', 'Mittel', 'Summe Symptom', 'Summe Wertigkeit'
        aggregated_df.rename(columns={
            'abbreviation': 'Kürzel',
            'description': 'Mittel',
            'total_occurrence': 'Summe Symptom',
            'total_degree': 'Summe Wertigkeit'
        }, inplace=True)

        # Sort by total_occurrence descending
        aggregated_df.sort_values(by='Summe Symptom', ascending=False, inplace=True)

        # Display the aggregated DataFrame
        st.write("**Gesammelte Mittel:**")
        st.table(aggregated_df)

        # Optionally, provide a download button for the results
        csv = aggregated_df.to_csv(index=False)
        st.download_button(
            label="Ergebnisse als CSV herunterladen",
            data=csv,
            file_name='final_analysis_results.csv',
            mime='text/csv',
        )

        # Button to restart the session (clear all states including final_results)
        if 'confirm_reset' not in st.session_state:
            st.session_state.confirm_reset = False

        if st.session_state.confirm_reset:
            st.warning(
                "Mit Klick auf 'Bestätigen' beginnst du eine komplett neue Analyse, alle bisherigen Analysen gehen dadurch verloren.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Bestätigen"):
                    full_reset_session_state()  # Call the full reset function
            with col2:
                if st.button("Abbrechen"):
                    st.session_state.confirm_reset = False
        else:
            if st.button("Neue Analyse starten"):
                st.session_state.confirm_reset = True
                st.rerun()

    else:
        st.write("Keine Remedies in den finalen Ergebnissen.")