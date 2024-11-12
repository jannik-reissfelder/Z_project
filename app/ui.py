import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from helpers import get_remedies, partial_reset_session_state, full_reset_session_state, add_to_final_results, remove_from_final_results
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
            # the user input to st.session_state.conversation
            st.session_state.conversation.append({"role": "user", "content": f"User Input: {st.session_state.user_input_symptom_class}"})
            st.rerun()
        else:
            st.warning("Bitte geben Sie die Symptomklasse des Patienten ein.")



def display_symptom_class_results():
    """
    Displays the results from the symptom class processing and provides a button to proceed.
    """
    # Custom smaller header using HTML
    st.markdown(
        "<h3 style='text-align: left; color: #333333;'>Ergebnisse der Symptomklassenanalyse</h3>",
        unsafe_allow_html=True
    )

    # Add horizontal separator below header
    st.markdown("---")

    # Retrieve outputs from session state
    oberkategorie = st.session_state.get('oberkategorie', 'Nicht verfügbar')
    unterkategorie = st.session_state.get('unterkategorie', 'Nicht verfügbar')
    suchpfad = st.session_state.get('suchpfad', 'Nicht verfügbar')
    begründung = st.session_state.get('begründung', 'Nicht verfügbar')
    user_input = st.session_state.get('user_input_symptom_class', 'Nicht verfügbar')

    # Use columns with vertical dividers and aligned content
    col1, col2, col3 = st.columns([1, 0.5, 0.5])  # Adjust column widths as necessary

    with col1:
        st.markdown("**Eingabe-Symptom**")
        st.write(user_input)

    with col2:
        st.markdown("**Oberkategorie**")
        st.write(oberkategorie)

    with col3:
        st.markdown("**Unterkategorie**")
        st.write(unterkategorie)

    # Add horizontal separator
    st.markdown("---")

    # Display suchpfad in its own section with bold heading
    st.markdown("**Suchpfad**")
    st.write(suchpfad)

    # Add another separator
    st.markdown("---")

    # Display Begründung in its own section with bold heading
    st.markdown("**Begründung**")
    st.write(begründung)

    # Add another separator
    st.markdown("---")

    # Create columns for layout
    col1, col2 = st.columns([1, 2])

    with col1:
        # Option 1: Proceed to the 'search' step
        if st.button("Analyse ist OK - Suchpfad finden."):
            st.session_state.current_step = 'search'
            st.rerun()

    with col2:
        # Option 2: Provide feedback for adjustment
        st.write("Analyse gefällt dir nicht? Bitte gib deine Anpassungen ein.")
        user_feedback = st.text_area("Anpassungen:", key='user_feedback')

        # Button to submit feedback
        if st.button("Anpassungen einreichen"):
            if user_feedback:
                # Append the user's feedback to the conversation
                st.session_state.conversation.append({"role": "user", "content": user_feedback})
                # Update the user input in session state
                st.session_state.user_input_symptom_class = user_feedback
                # Clear previous outputs if necessary
                st.session_state.oberkategorie = ''
                st.session_state.unterkategorie = ''
                st.session_state.suchpfad = ''
                st.session_state.begründung = ''
                # Set the state back to processing
                st.session_state.current_step = 'processing_symptom_class'
                st.rerun()
            else:
                st.warning("Bitte gib deine Anpassungen ein oder klicke auf 'Weiter' um fortzufahren.")




def adjust_symptom_class():
    st.title("Symptom Analyse Anpassung")
    st.write("Der Suchpfad und die Analyse gefallen dir nicht? Bitte erkläre, was du ändern möchtest.")

    user_input = st.text_area(
        "Bitte beschreibe das Symptom des Patienten erneut oder gib weitere Details an:",
        value=st.session_state.user_input_symptom_class
    )

    if st.button("Symptom erneut analysieren"):
        if user_input:
            # Update the user input in session state
            st.session_state.user_input_symptom_class = user_input
            # Append the new input to the conversation
            st.session_state.conversation.append({"role": "user", "content": user_input})
            # Clear previous outputs if necessary
            st.session_state.oberkategorie = ''
            st.session_state.unterkategorie = ''
            st.session_state.suchpfad = ''
            st.session_state.begründung = ''
            # Set the state back to processing
            st.session_state.current_step = 'processing_symptom_class'
            st.rerun()
        else:
            st.warning("Bitte geben Sie die Symptomklasse des Patienten ein.")





def display_remedies():
    """
    Displays selected symptoms and their remedies, and allows the user to include/exclude remedies
    in the final results using a checkbox.
    """
    st.write("**Ausgewählte Symptome:**")

    # Retrieve selected rows
    selected_rows = st.session_state.selected_rows

    if selected_rows is not None and not selected_rows.empty:
        for i, row in selected_rows.iterrows():
            symptom_id = row['id']
            symptom_text = row['path']

            # Unique keys for session state
            remedies_key = f'remedies_{symptom_id}'
            include_key = f'include_remedies_{symptom_id}'
            expanded_key = f'expanded_{symptom_id}'
            include_prev_key = f'include_remedies_{symptom_id}_prev'

            # Initialize expanded state
            if expanded_key not in st.session_state:
                st.session_state[expanded_key] = False  # Default is collapsed

            # Fetch remedies and store in session state if not already fetched
            if remedies_key not in st.session_state:
                remedies = get_remedies(symptom_id)
                st.session_state[remedies_key] = remedies
            else:
                remedies = st.session_state[remedies_key]

            # Initialize inclusion flag in session state
            if include_key not in st.session_state:
                st.session_state[include_key] = False  # Default is not included

            # Initialize previous include value
            if include_prev_key not in st.session_state:
                st.session_state[include_prev_key] = False

            # Set the expanded parameter based on session state
            with st.expander(f"Symptom ID: {symptom_id} - {symptom_text}", expanded=st.session_state[expanded_key]):
                if remedies:
                    # Display remedies as a sorted table
                    remedies_df = pd.DataFrame(remedies)
                    remedies_df.rename(columns={
                        'abbreviation': 'Kürzel',
                        'description': 'Mittel',
                        'degree': 'Wertigkeit'
                    }, inplace=True)
                    remedies_df = remedies_df.sort_values(by='Wertigkeit', ascending=False)
                    st.table(remedies_df)

                    # Checkbox to include/exclude remedies in final results
                    include = st.checkbox(
                        "Mittel zu den finalen Ergebnissen hinzufügen",
                        key=include_key  # Use include_key without loop index
                    )

                    # Handle inclusion/exclusion
                    if include != st.session_state[include_prev_key]:
                        # Inclusion state has changed
                        if include:
                            # Checkbox is checked, add remedies
                            add_to_final_results(remedies, symptom_id)
                            st.session_state[expanded_key] = True
                        else:
                            # Checkbox is unchecked, remove remedies
                            remove_from_final_results(symptom_id)
                            st.session_state[expanded_key] = True

                        # Update previous include value
                        st.session_state[include_prev_key] = include

                else:
                    st.write("Keine Mittel für dieses Symptom gefunden.")

        # Separator
        st.markdown("---")

        # Button to return to symptom search (partial reset)
        if st.button("Zurück zur Symptom Suche"):
            partial_reset_session_state()

        # Button to proceed to final analysis
        if st.button("Weiter zu Finalem Analyse Ergebnis"):
            st.session_state.current_step = 'final_analysis'
            st.rerun()
    else:
        st.write("Keine Symptome ausgewählt.")







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

        # Sort by 'Summe Symptom' and then by 'Summe Wertigkeit' both in descending order
        aggregated_df.sort_values(by=['Summe Symptom', 'Summe Wertigkeit'], ascending=[False, False], inplace=True)

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