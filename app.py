# app.py

import requests
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import json
from flask import Flask, render_template, request
from utils import *
import yaml

# Load the YAML file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Access values
generative_url = config["generative"]


app = Flask(__name__)


def get_generated_image(data):
    """
    ATTEMPTS to call the real URL. If it fails, it creates a DUMMY image.
    This makes the app runnable even if the image generation service is down.
    """
    url = generative_url
    
    response = requests.post(url, json=data)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))

# --- Helper Function to Convert Image to Data URL ---

def pil_to_base64_url(pil_image, format="PNG"):
    """Converts a PIL.Image object to a Base64 encoded Data URL."""
    buffered = BytesIO()
    pil_image.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{img_str}"

# A placeholder for broken image links
PLACEHOLDER_WHITE_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/8/84/Bianco.png"

# --- Main Flask Route ---

@app.route('/')
def display_results():
    data_str = request.args.get('data')
    if not data_str:
        return "<h1>Error: No data provided. Please use sender.html</h1>", 400

    try:
        data = json.loads(data_str)
    except json.JSONDecodeError:
        return "<h1>Error: Invalid data format.</h1>", 400

    # 1. Run all backend processing functions
    df_all_materials = retrieve_available_materials()
    df_resume = selection_resume(data, df_all_materials)
    
    if (df_resume['sostenibilita'] == 3).all():

        return render_template('alternative_index.html')

    nuova_proposta_1, tabella_nuova_proposta_1 = elabora_nuova_proposta(data, df_all_materials, df_resume)
    nuova_proposta_2, tabella_nuova_proposta_2 = elabora_nuova_proposta(data, df_all_materials, df_resume)
    print(nuova_proposta_1)
    
    # 2. Process images
    # Image 1 is just a URL from the input data
    feedback_photo_url = data.get("feedback_photo_url", PLACEHOLDER_WHITE_IMAGE_URL)
    
    # Images 2 and 3 are generated and converted to Data URLs
    im1_pil = get_generated_image(nuova_proposta_1)
    im2_pil = get_generated_image(nuova_proposta_2)
    
    generated_image_1_url = pil_to_base64_url(im1_pil) if im1_pil else PLACEHOLDER_WHITE_IMAGE_URL
    generated_image_2_url = pil_to_base64_url(im2_pil) if im2_pil else PLACEHOLDER_WHITE_IMAGE_URL

    # 3. Process tables (convert DataFrames to HTML strings)
    table_1_html = df_resume.to_html(classes='data-table', index=False)
    table_2_html = tabella_nuova_proposta_1.to_html(classes='data-table', index=False)
    table_3_html = tabella_nuova_proposta_2.to_html(classes='data-table', index=False)

    # 4. Pack everything into a context dictionary to send to the template
    context = {
        "feedback_photo_url": feedback_photo_url,
        "generated_image_1_url": generated_image_1_url,
        "generated_image_2_url": generated_image_2_url,
        "table_1_html": table_1_html,
        "table_2_html": table_2_html,
        "table_3_html": table_3_html,
        "placeholder_image_url": PLACEHOLDER_WHITE_IMAGE_URL
    }

    return render_template('index.html', **context)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True, port=5010)