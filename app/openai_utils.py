# openai_utils.py

import openai
from helpers import get_secret, initialize_openai  # Assuming get_secret is in helpers.py
import json
# Initialize OpenAI client
client = initialize_openai()

# fucntion to init messages
def init_messages():
    return [
            {
                "role": "system",
                "content": [
                    {
                        "text": "Ordne die gegebenen Symptome in die passendste Ober- und Unterkategorie der homöopathischen Einteilung nach dem deutschen Synthesis zu.\n\nWähle zuerst eine der Oberkategorien: \"Gemüt\", \"Körper\", \"Allgemein\". Falls die Kategorie \"Körper\" zutrifft, wähle aus der detaillierteren Liste die spezifische Unterkategorie. Basiere deine Entscheidung auf einer genauen Analyse des Symptoms.\n\n# Schritte\n\n1. **Analyse des Symptoms**: Lies das gegebene Symptom sorgfältig und analysiere, welchen Körperteil, Zustand, oder emotionale Zustand es betrifft.\n2. **Bestimmen der Oberkategorie**:\n   - Falls das Symptom emotionaler oder psychologischer Natur ist, ordne es in die Kategorie \"Gemüt\" ein.\n   - Falls das Symptom einen körperlichen Aspekt hat, wechsle zur detaillierten Auswahl unter der Kategorie \"Körper\".\n   - Falls das Symptom allgemeiner Natur ist, ordne es in die Kategorie \"Allgemein\" ein.\n3. **Wahl der Unterkategorie bei Körper-Symptomen**: Ordne das Symptom einer der spezifischen Unterkategorien des Körpers zu. Sei dabei so spezifisch wie möglich.\n4. **Begründung der Entscheidung**: Stelle eine kurze Begründung zur Wahl der Ober- und Unterkategorie bereit.\n\n# Output Format\n\nDas Ergebnis sollte in folgender JSON-Struktur formatiert sein:\n\n```json\n{\n  \"Symptom\": \"[Beschreibung des Symptoms]\",\n  \"Oberkategorie\": \"[Gemüt | Körper | Allgemein]\",\n  \"Unterkategorie\": \"[spezifische Unterkategorie oder 'Nicht anwendbar']\",\n  \"Begründung\": \"[Kurze Begründung für diese Einordnung]\"\n}\n```\n\n# Beispiele\n\n**Beispiel 1:**\n- **Input**: \"Der Patient fühlt eine schwere Angst vor der Dunkelheit.\"\n- **Output**:\n  ```json\n  {\n    \"Symptom\": \"Der Patient fühlt eine schwere Angst vor der Dunkelheit\",\n    \"Oberkategorie\": \"Gemüt\",\n    \"Unterkategorie\": \"Nicht anwendbar\",\n    \"Begründung\": \"Das Symptom ist psychischer Natur und beschreibt eine emotionale Angst, daher gehört es in die Kategorie 'Gemüt'.\"\n  }\n  ```\n\n**Beispiel 2:**\n- **Input**: \"Der Patient hat pochende Schmerzen im Bereich der rechten Schläfe.\"\n- **Output**:\n  ```json\n  {\n    \"Symptom\": \"Der Patient hat pochende Schmerzen im Bereich der rechten Schläfe\",\n    \"Oberkategorie\": \"Körper\",\n    \"Unterkategorie\": \"Kopf\",\n    \"Begründung\": \"Das Symptom betrifft Schmerzen im Kopf- bzw. Schläfenbereich, daher wird es in die Unterkategorie 'Kopf' eingeordnet.\"\n  }\n  ```\n\n**Beispiel 3:**\n- **Input**: \"Ein allgemeines Gefühl der Kälte im gesamten Körper.\"\n- **Output**:\n  ```json\n  {\n    \"Symptom\": \"Ein allgemeines Gefühl der Kälte im gesamten Körper\",\n    \"Oberkategorie\": \"Allgemein\",\n    \"Unterkategorie\": \"Nicht anwendbar\",\n    \"Begründung\": \"Das Symptom ist systemisch und betrifft den Gesamtzustand, daher gehört es in die Kategorie 'Allgemein'.\"\n  }\n  ```\n\n**Beachte:** Die Entscheidung für eine Kategorie sollte logisch fundiert sein und immer eine sinnvolle Begründung enthalten.",
                        "type": "text"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "text": "Der Patient betet bei Nacht.",
                        "type": "text"
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "text": "```json\n{\n  \"Symptom\": \"Der Patient betet bei Nacht\",\n  \"Oberkategorie\": \"Gemüt\",\n  \"Unterkategorie\": \"Nicht anwendbar\",\n  \"Begründung\": \"Das Symptom beschreibt ein Verhalten oder eine Gewohnheit, die aus einem mentalen oder emotionalen Zustand resultiert. Daher wird es in die Kategorie 'Gemüt' eingeordnet.\"\n}\n```",
                        "type": "text"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Der Patient hat Trennungsangst"
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "{\"Symptom\":\"Der Patient hat Trennungsangst\",\"oberKategorie\":\"Gemüt\",\"unterKategorie\":\"Nicht anwendbar\",\"Begründung\":\"Trennungsangst ist eine emotionale Reaktion und betrifft den psychologischen Zustand des Patienten, daher gehört dieses Symptom in die Kategorie 'Gemüt'.\"}"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Der Patient hat eine Kehlkopfentzündung"
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "{\"Symptom\":\"Der Patient hat eine Kehlkopfentzündung\",\"oberKategorie\":\"Körper\",\"unterKategorie\":\"Kehlkopf und Trachea\",\"Begründung\":\"Das Symptom betrifft eine Entzündung im Bereich des Kehlkopfes, was eine spezifische körperliche Erkrankung ist. Daher gehört es in die Unterkategorie 'Kehlkopf und Trachea' des Körpers.\"}"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Der Patient klagt über Schlaflosigkeit am frühen Morgen"
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "{\"Symptom\":\"Der Patient klagt über Schlaflosigkeit am frühen Morgen\",\"oberKategorie\":\"Körper\",\"unterKategorie\":\"Schlaf\",\"Begründung\":\"Das Symptom betrifft ein Problem mit dem Schlaf, insbesondere das frühe Erwachen und die daraus resultierende Schlaflosigkeit. Daher ordnen wir es in die Unterkategorie 'Schlaf' ein.\"}"
                    }
                ]
            }
        ]


# Placeholder for the new function
def process_symptom_class(user_input):
    """
    Processes the symptom class by making a call to OpenAI's model.

    Parameters:
    - user_input (str): The input provided by the user.

    Returns:
    - response (str): The response from OpenAI's model.
    """

    # init messages
    messages = init_messages()
    # init client
    client = initialize_openai()

    response_content = client.chat.completions.create(
        model="gpt-4o",
        messages= messages + [{ "role": "user", "content": [ { "text": user_input, "type": "text" }] }],
        temperature=0.1,
        max_tokens=200,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "kategorie_schema",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "Symptom": {
                            "type": "string",
                            "description": "Gib den Input also das Symptom wieder."
                        },
                        "oberKategorie": {
                            "type": "string",
                            "description": "Die gewählte Oberkategorie auf Basis des Symptoms.",
                            "enum": [
                                "Gemüt",
                                "Körper",
                                "Allgemein"
                            ]
                        },
                        "unterKategorie": {
                            "type": "string",
                            "description": "Die spezifische Unterkategorie, falls 'Körper' als Oberkategorie gewählt wird. Falls es sich um 'Gemüt' handelt, wähle 'Nicht anwendbar' aus.",
                            "enum": [
                                "Schwindel",
                                "Kopf",
                                "Auge",
                                "Sehen",
                                "Ohr",
                                "Hören",
                                "Nase",
                                "Gesicht",
                                "Mund",
                                "Zähne",
                                "Innerer Hals",
                                "Äußerer Hals",
                                "Äußerer Hals und Nacken",
                                "Magen",
                                "Abdomen",
                                "Rektum",
                                "Stuhl",
                                "Blase",
                                "Nieren",
                                "Prostata",
                                "Harnröhre",
                                "Urin",
                                "Harnorgane",
                                "Männliche Genitalien",
                                "Weibliche Genitalien",
                                "Genitalien und Sexualität",
                                "Kehlkopf und Trachea",
                                "Atmung",
                                "Husten",
                                "Auswurf",
                                "Brust",
                                "Rücken",
                                "Extremitäten",
                                "Schlaf",
                                "Träume",
                                "Frost",
                                "Fieber",
                                "Schweiß",
                                "Haut",
                                "Nicht anwendbar"
                            ]
                        },
                        "Begründung": {
                            "type": "string",
                            "description": "Die spezifische Unterkategorie, falls 'Körper' als Oberkategorie gewählt wird."
                        }
                    },
                    "required": [
                        "Symptom",
                        "oberKategorie",
                        "unterKategorie",
                        "Begründung"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )
    # Return the response
    response_dict = response_content.choices[0].message.content
    # load json
    response_dict = json.loads(response_dict)
    return  response_dict.get("oberKategorie"), response_dict.get("unterKategorie"), response_dict.get("Begründung")


# Function to enrich query using LLM
def enrich_query(conversation):
    opai_client = initialize_openai()
    response = opai_client.chat.completions.create(
        model="gpt-4o",
        messages=conversation,
        max_tokens=50,
        temperature=0.1
    )

    enriched_query = response.choices[0].message.content.strip()
    return enriched_query