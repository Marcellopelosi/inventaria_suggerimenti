import requests
import pandas as pd
import yaml

# Load the YAML file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Access values
generative_url = config["generative"]
db = config["db"]


#Da mostrare con l'immagine corrispondente all'url, le stelle in numero pari al numero indicato nella sostenibilità e uno sfondo verde chiaro
#per tutta la riga nel caso in cui la sostenibilita sia 3, arancione chiaro se è 2 e rosso chiaro se è 1.

def retrieve_available_materials():
    url = db
    response = requests.get(url)
    df = pd.DataFrame(response.json())
    sostenibilita = pd.read_csv("sostenibilita.csv")

    return pd.merge(df, sostenibilita, on="photo_url", how="left")

def selection_resume(data, df):
    return df[df["photo_url"].isin([i["photo_url"] for i in data["materials"]])][["name", "photo_url", "sostenibilita","material_type"]]

def elabora_nuova_proposta(data, df, df_resume):
    nuova_proposta = data.copy()
    materiali_nuova_proposta = []
    tabella_nuove_proposte = []
    materiali_richieste_non_sostenibili = df_resume[df_resume["sostenibilita"]<3]["material_type"].to_list()
    richieste_sostenibili = df_resume[df_resume["sostenibilita"]==3].reset_index(drop = True)
    materiale_sostenibile = df[df["sostenibilita"]==3]
    for r in materiali_richieste_non_sostenibili:
        materiale_selezionato = materiale_sostenibile[materiale_sostenibile["material_type"] == r].sample(1)
        materiale_selezionato = materiale_selezionato[['name', 'sostenibilita', 'id', 'material_type', 'available_quantity',
       'photo_url', 'fabric_category', 'fabric_subcategory']]
        tabella_nuove_proposte.append(materiale_selezionato)
        materiali_nuova_proposta.append({"name":materiale_selezionato.name.values[0] ,
                                        "photo_url":materiale_selezionato.photo_url.values[0]})
        
        
    for i in range(len(richieste_sostenibili)):
        materiali_nuova_proposta.append({"name":richieste_sostenibili.loc[i]["name"] ,
                                        "photo_url":richieste_sostenibili.loc[i]["photo_url"]})
        
    nuova_proposta["materials"] = materiali_nuova_proposta

    if len(tabella_nuove_proposte) >= 1:
        tabella_nuove_proposte = pd.concat(tabella_nuove_proposte)
    else:
        tabella_nuove_proposte = tabella_nuove_proposte[0]
        

    return nuova_proposta, tabella_nuove_proposte

import requests
from PIL import Image
from io import BytesIO

def get_generated_image(data):
    url = generative_url

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()

        # Convert binary content to PIL image
        image = Image.open(BytesIO(response.content))
        return image  # You can now use this image variable in memory

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except Exception as e:
        print(f"Error processing image: {e}")
        return None
