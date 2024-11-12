# openai_utils.py

import openai
from helpers import initialize_openai  # Assuming get_secret is in helpers.py
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
          "text": "Analysiere die Symptom-Beschreibung des Patienten oder der Patientin nach deutschem Synthesis aus homöopathischer Perspektive. Das oberste Ziel den idealen Suchpfad nach Synthesis bestens zu finden.\n\nIm ersten Schritt soll die Symptombeschreibung  in die passenden Ober- und Unterkategorie der homöopathischen Einteilung nach dem deutschen Synthesis eingeteilt werden.\n\nWähle zuerst eine der Oberkategorien: \"Gemüt\", \"Körper\", \"Allgemeines\". Falls die Kategorie \"Körper\" zutrifft, wähle aus der detaillierteren Liste die spezifische Unterkategorie. Basiere deine Entscheidung auf einer genauen Analyse der Symptombeschreibung.\n\n# Schritte\n\n1. **Analyse des Symptom-Beschreibung**: Lies die Beschreibung sorgfältig und analysiere, welchen Körperteil, Zustand, oder emotionale Zustand es betrifft.\n2. **Bestimmen der Oberkategorie**:\n   - Falls das Symptom emotionaler oder psychologischer Natur ist, ordne es in die Kategorie \"Gemüt\" ein.\n   - Falls das Symptom einen körperlichen Aspekt hat, wechsle zur detaillierten Auswahl unter der Kategorie \"Körper\".\n   - Falls das Symptom allgemeiner Natur ist, ordne es in die Kategorie \"Allgemein\" ein.\n3. **Wahl der Unterkategorie bei Körper-Symptomen**: Ordne das Symptom einer der spezifischen Unterkategorien des Körpers zu. Sei dabei so spezifisch wie möglich.\n4. **Suchpfad**: Gebe so präzise wie möglich den abgeleiteten Suchpfad wieder, um das passende Mittel auf Basis der Symptombeschreibung im Synthesis zu finden.\n5. **Begründung**: Stelle eine kurze Begründung zur Wahl der Ober- und Unterkategorie bereit, als auch für den ausgegebenen Suchpfad.\n\n# Output Format\n\nDas Ergebnis sollte in folgender JSON-Struktur formatiert sein:\n\n```json\n{\n  \"Symptom\": \"[Beschreibung des Symptoms]\",\n  \"Oberkategorie\": \"[Gemüt | Körper | Allgemeines]\",\n  \"Unterkategorie\": \"[spezifische Unterkategorie oder 'Nicht anwendbar']\",\n\"Suchpfad\": \"[Präziser Suchpfad nach Synthesis]\",\n  \"Begründung\": \"[Kurze Begründung für diese Einordnung]\"\n}\n```\n# Beispiele\n\n**Beispiel 1:**\n- **Input**: \"Der Patient klagt über schlechten Schlaf und das er morgens nicht erfrischt ist.\"\n- **Output**:\n  ```json\n {\n  \"Symptom\": \"Der Patient klagt über schlechten Schlaf und das er morgens nicht erfrischt ist.\",\n  \"Oberkategorie\": \"Allgemeines\",\n  \"Unterkategorie\": \"Nicht anwendbar\",\n  \"Suchpfad\": \"Allgemeines - Erwachen- nach , agg.\",\n  \"Begründung\": \"Das Symptom betrifft den allgemeinen Zustand des Schlafes und dessen Qualität, was in die Kategorie 'Allgemeines' fällt. Es handelt sich nicht um ein spezifisches körperliches Symptom oder ein Gemütszustand, sondern um eine allgemeine Beschwerde über den Schlaf und das Gefühl der Erfrischung am Morgen.\"\n}\n  ```",
          "type": "text"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "text": "Aufwachen ohne Schwitzen zwischen 3 und 4 Uhr morgens.",
          "type": "text"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "\n  {\n  \"Symptom\": \"Aufwachen ohne Schwitzen zwischen 3 und 4 Uhr morgens.\",\n  \"Oberkategorie\": \"Allgemeines\",\n  \"Unterkategorie\": \"Nicht anwendbar\",\n  \"Suchpfad\": \"Allgemeines - Erwachen - Zeit - 3 bis 4 Uhr morgens\",\n  \"Begründung\": \"Das Symptom beschreibt ein spezifisches Erwachen zu einer bestimmten Zeit, was in die Kategorie 'Allgemeines' fällt. Es handelt sich nicht um ein körperliches Symptom oder ein Gemütszustand, sondern um eine allgemeine Beschwerde über das Erwachen zu einer bestimmten Uhrzeit.\"\n}",
          "type": "text"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "text": "gut aber, aber das gehört für mich eher in die Kategorie Schlaf anstatt Alggemeines",
          "type": "text"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "\n  {\n  \"Symptom\": \"Aufwachen ohne Schwitzen zwischen 3 und 4 Uhr morgens.\",\n  \"Oberkategorie\": \"Körper\",\n  \"Unterkategorie\": \"Schlaf\",\n  \"Suchpfad\": \"Körper - Schlaf - Erwachen - Zeit - 3 bis 4 Uhr morgens\",\n  \"Begründung\": \"Das Symptom betrifft den Schlaf und das spezifische Erwachen zu einer bestimmten Zeit, was in die Unterkategorie 'Schlaf' unter der Oberkategorie 'Körper' fällt. Es handelt sich um ein spezifisches Schlafmuster, das in der homöopathischen Analyse unter Schlafstörungen eingeordnet wird.\"\n}",
          "type": "text"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "text": "Ah Verzeihe, \"Körper\" ist niemals teil des Suchpfads. Wenn du zu dem Schluss kommst, das es sich um die Kategorie \"Körper\" handelt, dann beginnt der Suchpfad stets mit der entsprechenden Unterkategorie.",
          "type": "text"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "\n  {\n  \"Symptom\": \"Aufwachen ohne Schwitzen zwischen 3 und 4 Uhr morgens.\",\n  \"Oberkategorie\": \"Körper\",\n  \"Unterkategorie\": \"Schlaf\",\n  \"Suchpfad\": \"Schlaf - Erwachen - Zeit - 3 bis 4 Uhr morgens\",\n  \"Begründung\": \"Das Symptom betrifft den Schlaf und das spezifische Erwachen zu einer bestimmten Zeit, was in die Unterkategorie 'Schlaf' fällt. Es handelt sich um ein spezifisches Schlafmuster, das in der homöopathischen Analyse unter Schlafstörungen eingeordnet wird.\"\n}",
          "type": "text"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "text": "Der Patient hat die Neigung die Zähne zusammenzubeißen, sodass einzelne einzelne Zähne tagsüber weh tun.",
          "type": "text"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "\n  {\n  \"Symptom\": \"Der Patient hat die Neigung die Zähne zusammenzubeißen, sodass einzelne Zähne tagsüber weh tun.\",\n  \"Oberkategorie\": \"Körper\",\n  \"Unterkategorie\": \"Zähne\",\n  \"Suchpfad\": \"Zähne - Schmerzen - durch Zusammenbeißen\",\n  \"Begründung\": \"Das Symptom betrifft die Zähne und den Schmerz, der durch das Zusammenbeißen entsteht. Es handelt sich um ein körperliches Symptom, das in die Unterkategorie 'Zähne' eingeordnet wird, da es spezifisch die Zahnschmerzen durch das Zusammenbeißen beschreibt.\"\n}",
          "type": "text"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "text": "Sehr gut, hier geht es aber tatsächlich eher um das Beißen, statt den Schmerz per se.",
          "type": "text"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "\n  {\n  \"Symptom\": \"Der Patient hat die Neigung die Zähne zusammenzubeißen, sodass einzelne Zähne tagsüber weh tun.\",\n  \"Oberkategorie\": \"Körper\",\n  \"Unterkategorie\": \"Zähne\",\n  \"Suchpfad\": \"Zähne - Beißen - Neigung zum Zusammenbeißen\",\n  \"Begründung\": \"Das Symptom betrifft das unwillkürliche Zusammenbeißen der Zähne, was zu Schmerzen führt. Daher liegt der Fokus auf der Handlung des Beißens, was in die Unterkategorie 'Zähne' fällt. Es beschreibt die Neigung zum Zusammenbeißen, was die primäre Ursache der Beschwerden ist.\"\n}",
          "type": "text"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Patient entwickelt bei viel Druck Kopfschmerzen, von der Stirn zum Hinterkopf, manchmal von Schläfe zu Schläfe."
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "{\"Symptom\":\"Patient entwickelt bei viel Druck Kopfschmerzen, von der Stirn zum Hinterkopf, manchmal von Schläfe zu Schläfe.\",\"Oberkategorie\":\"Körper\",\"Unterkategorie\":\"Kopf\",\"Suchpfad\":\"Kopf - Schmerzen - Druck - Stirn bis Hinterkopf - Schläfe zu Schläfe\",\"Begründung\":\"Das Symptom beschreibt Kopfschmerzen, die durch Druck entstehen und sich von der Stirn zum Hinterkopf sowie von Schläfe zu Schläfe ausbreiten. Es handelt sich um ein körperliches Symptom, das in die Unterkategorie 'Kopf' eingeordnet wird, da es spezifisch die Art und den Verlauf der Kopfschmerzen beschreibt.\"}"
        }
      ]
    }
  ]


# Placeholder for the new function
def process_symptom_class(user_input, conversation):
    """
    Processes the symptom class by making a call to OpenAI's model.

    Parameters:
    - user_input (str): The input provided by the user.

    Returns:
    - response (str): The response from OpenAI's model.
    """

    # init messages
    messages = conversation
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
            "required": [
              "Symptom",
              "Oberkategorie",
              "Unterkategorie",
              "Suchpfad",
              "Begründung"
            ],
            "properties": {
              "Symptom": {
                "type": "string",
                "description": "Gib den Input also das Symptom nochmal wieder."
              },
              "Oberkategorie": {
                "enum": [
                  "Gemüt",
                  "Körper",
                  "Allgemein"
                ],
                "type": "string",
                "description": "Die gewählte Oberkategorie auf Basis des Symptoms."
              },
              "Unterkategorie": {
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
                ],
                "type": "string",
                "description": "Die spezifische Unterkategorie, falls 'Körper' als Oberkategorie gewählt wird. Falls es sich um 'Gemüt' handelt, wähle 'Nicht anwendbar' aus."
              },
              "Suchpfad": {
                "type": "string",
                "description": "Präziser Suchpfad."
              },
              "Begründung": {
                "type": "string",
                "description": "Begründung des Suchpfads und der Kategorien."
              }
            },
            "additionalProperties": False
            }
          }

        }
    )
    # Return the response
    response_dict_raw = response_content.choices[0].message.content
    # load json
    response_dict = json.loads(response_dict_raw)
    return  response_dict.get("Oberkategorie"), response_dict.get("Unterkategorie"), response_dict.get("Suchpfad"), response_dict.get("Begründung"), response_dict_raw

