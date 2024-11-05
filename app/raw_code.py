import openai
import boto3
import json
import os
from openai import OpenAI
import pandas as pd
import numpy as np
from tenacity import retry, wait_random_exponential, stop_after_attempt
from tqdm import tqdm


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
    print(json.loads(secret)["OPENAI_KEY"])
    return json.loads(secret)["OPENAI_KEY"]

os.environ["OPENAI_API_KEY"] = get_secret()
client = OpenAI()

# load data with embeddings
data = pd.read_parquet("trial_sym_rem_embeddings.gz")



@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embeddings(texts, model="text-embedding-3-small"):
    response = openai.embeddings.create(input=texts, model=model)
    return [item.embedding for item in response.data]


def search_top_similar_symptoms(user_query, data, top_n=10):
    # Schritt 1: Benutzereingabe entgegennehmen und bereinigen (optional)
    # Hier nehmen wir den Text direkt

    # Schritt 2: Embedding für die Benutzereingabe generieren
    user_embedding = get_embeddings([user_query])[0]  # Annahme: get_embeddings gibt eine Liste von Embeddings zurück

    # Schritt 3: Vorbereitung der gespeicherten Embeddings
    # Konvertiere die Embeddings-Spalte zu einem 2D-NumPy-Array, falls noch nicht geschehen
    # Angenommen, 'embeddings' sind als Listen gespeichert
    embeddings_matrix = np.vstack(data['embeddings'].values)

    # Schritt 4: Berechnung der Kosinusähnlichkeit ohne Normalisierung
    cosine_similarities = np.dot(embeddings_matrix, user_embedding)

    # Schritt 5: Sortierung und Auswahl der Top-N ähnlichen Einträge
    top_indices = cosine_similarities.argsort()[::-1][:top_n]
    top_scores = cosine_similarities[top_indices]
    top_symptoms = data.iloc[top_indices].copy()
    top_symptoms['similarity'] = top_scores


    # Schritt 7: Präsentation der Ergebnisse
    return top_symptoms



def enrich_query(conversation):
    """
    Generates an enriched query using the LLM based on the provided conversation history.
    
    Args:
        conversation (list of dict): The conversation history.
        
    Returns:
        str: The enriched query generated by the assistant.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation,
        max_tokens=30,
        temperature=0.1
    )
    
    enriched_query = response.choices[0].message.content.strip()
    return enriched_query


system_message = "Du bist deutscher Homöopath und analysierst die Symptome des Patienten nach dem Buch des Synthesis."


def main_workflow():
    """
    Main workflow that handles user interaction for enriching and adjusting queries.
    
    Args:
        data (pd.DataFrame): DataFrame containing 'embeddings' and 'symptom' columns.
    """
    # Initialize conversation history with the specified initial messages
    conversation = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": "Extrahiere die Symptome des Patienten und paraphrasiere die Symptomatik falls zutreffend nach dem deutschen Synthesis Buch der Homöopathen. Bitte die Schlüssel-Symptome nach Synthesis extrahieren, gerne Komma separiert. Bitte NUR die Symptomatik geben, kurz und präzise."},
        {"role": "user", "content": "Bitte antworte als würdest du versuchen so präzise wie möglich den Suchpfad im Synthesis zu finden, auf Basis der Symptomatik."},
    ]

    # Step 1: Get initial user input
    user_input = input("Bitte geben Sie die Symptome des Patienten ein: ").strip()
    conversation.append({"role": "user", "content": f"User Input: {user_input}"})

    # Step 2: Generate initial enriched query
    enriched_query = enrich_query(conversation)
    conversation.append({"role": "assistant", "content": enriched_query})
    print("\nEnriched Query Vorschlag:", enriched_query)

    while True:
        # Step 3: Ask user if they want to adjust the enriched query
        user_feedback = input("\nMöchten Sie das vorgeschlagene Symptomset anpassen? (Ja/Nein): ").strip().lower()
        
        if user_feedback in ["nein", "n", "no"]:
            print("Bestätigte Anfrage:", enriched_query)
            break
        elif user_feedback in ["ja", "j", "yes", "y"]:
            adjustment = input("Bitte geben Sie die gewünschten Anpassungen ein (z.B. 'Entferne Schlaflosigkeit, füge Kopfschmerzen hinzu'): ").strip()
            conversation.append({"role": "user", "content": f"Anpassung: {adjustment}"})
            conversation.append({"role": "assistant", "content": "Bitte passe die erweiterten Symptome basierend auf den Benutzereingaben an."})
            
            # Re-generate the enriched query with adjustments
            enriched_query = enrich_query(conversation)
            conversation.append({"role": "assistant", "content": enriched_query})
            print("\nAngepasstes Enriched Query:", enriched_query)
        else:
            print("Bitte geben Sie 'Ja' oder 'Nein' ein.")

    # Step 4: Perform similarity search with final enriched query
    top_results = search_top_similar_symptoms(enriched_query, data, top_n=5)
    print("\nTop ähnliche Symptome:")
    print(top_results)


if __name__ == "__main__":
    main_workflow()