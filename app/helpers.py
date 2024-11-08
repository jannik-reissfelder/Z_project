# helpers.py

import openai
from openai import OpenAI
import boto3
import sqlite3
import json
import os
import pandas as pd
import numpy as np
from tenacity import retry, wait_random_exponential, stop_after_attempt
import streamlit as st

# Function to retrieve OpenAI API key from AWS Secrets Manager
def get_secret():
    secret_name = "openai/api-key/chat-app-keywords"
    region_name = "eu-central-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)["OPENAI_KEY"]

# Initialize OpenAI client
def initialize_openai():
    # os.environ["OPENAI_API_KEY"] = get_secret()
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_KEY"]
    # Return the OpenAI client instance if necessary
    client = OpenAI()
    return client

# Retry logic for getting embeddings
@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embeddings(texts, model="text-embedding-3-small"):
    response = openai.embeddings.create(input=texts, model=model)
    return [item.embedding for item in response.data]

# Function to search for top similar symptoms
def search_top_similar_symptoms(user_query, data, llm_oberkategorie, llm_unterkategorie, top_n=10):
    # first filter database on llm_oberkategorie or llm_unterkategorie
    if llm_oberkategorie == 'Körper':
        data = data[data['category'] == llm_unterkategorie]
    else:
        data = data[data['category'] == llm_oberkategorie]
    # after filtering get embeddings of user query
    user_embedding = get_embeddings([user_query])[0]
    # stack all embeddings of symptoms
    embeddings_matrix = np.vstack(data['relevant_symptom_embeddings'].values)
    # calculate cosine similarities
    cosine_similarities = np.dot(embeddings_matrix, user_embedding)
    # get top n similar symptoms
    top_indices = cosine_similarities.argsort()[::-1][:top_n]
    top_scores = cosine_similarities[top_indices]
    top_symptoms = data.iloc[top_indices].copy()
    top_symptoms['similarity'] = top_scores
    return top_symptoms


def get_remedies(symptom_id, db_path='synthesis.db'):
    """
    Retrieves remedies associated with a given symptom_id from the database.

    Parameters:
    - symptom_id (int): The ID of the symptom.
    - db_path (str): Path to the SQLite database file.

    Returns:
    - List of dictionaries containing remedy information and the associated symptom_id.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to get remedies associated with the symptom_id
    query = """
    SELECT remedies.remedy_abbreviation, remedies.description, symptom_remedies.degree
    FROM symptom_remedies
    JOIN remedies ON symptom_remedies.remedy_abbreviation = remedies.remedy_abbreviation
    WHERE symptom_remedies.symptom_id = ?;
    """

    cursor.execute(query, (symptom_id,))
    remedies = cursor.fetchall()

    # Close the connection
    conn.close()

    # Format the results
    return [{'abbreviation': r[0], 'description': r[1], 'degree': r[2], 'symptom_id': symptom_id} for r in remedies]

# helpers.py

def partial_reset_session_state():
    """
    Resets the session state variables to start a new symptom search,
    while preserving 'final_results' and 'conversation'.
    """
    # Variables to preserve
    variables_to_keep = ['final_results', 'conversation']

    # Get all keys in session state
    keys = list(st.session_state.keys())

    # Delete all keys except those to keep
    for key in keys:
        if key not in variables_to_keep:
            del st.session_state[key]

    # Set 'current_step' to 'input_symptom_class'
    st.session_state.current_step = 'input_symptom_class'

    # Rerun the app
    st.rerun()



def add_to_final_results(remedies, symptom_id):
    """
    Adds remedies to the final_results session state, tagging them with symptom_id.
    Parameters:
    - remedies (list of dict): List of remedies to add.
    - symptom_id (int): The ID of the symptom the remedies are associated with.
    """
    # Tag each remedy with the symptom_id
    for remedy in remedies:
        remedy_copy = remedy.copy()
        remedy_copy['symptom_id'] = symptom_id
        st.session_state.final_results.append(remedy_copy)

def remove_from_final_results(symptom_id):
    """
    Removes remedies associated with a specific symptom_id from the final_results session state.
    Parameters:
    - symptom_id (int): The ID of the symptom whose remedies should be removed.
    """
    st.session_state.final_results = [
        remedy for remedy in st.session_state.final_results
        if remedy.get('symptom_id') != symptom_id
    ]



def full_reset_session_state():
    """
    Resets the entire session state, effectively restarting the app.
    """
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
