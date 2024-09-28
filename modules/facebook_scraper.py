import requests
import json
import pandas as pd
import unicodedata
import re
from transformers import pipeline

# Token de acceso de la Graph API de Facebook
access_token = 'EAAGdiBedtwwBOxnDJg4M5BipNRGZAedOJjETEvWpVyZC61J70Mb8J2vrPKVZAqdrjylKMNLRy3C2tjYaSDIoWz3QfLCri6gUQBDV5GksgkR7ZAA5fEILAFVeI93d2amYs8PZB5ViQZCgobCaPBKiTOi5KbPiflKHlBuaWQsLpMKN9nLUp1zqEqd0Hpgb6L'
page_id = '392880987233705'

# URL base para acceder a la API de Graph
base_url = f"https://graph.facebook.com/v20.0/{page_id}/posts"

# Parámetros para la solicitud
params = {
    'access_token': access_token,
    'fields': 'id,message,created_time,comments{message,from,created_time}'
}

def clean_text(text):
    """
    Limpia el texto eliminando acentos, caracteres especiales y convirtiéndolo a minúsculas.
    """
    text = text.lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text

def get_facebook_posts_and_comments():
    all_data = []
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', [])
            
            for post in posts:
                post_id = post['id']
                post_message = post.get('message', 'No message')
                post_created_time = post['created_time']
                comments_data = []

                if 'comments' in post:
                    comments = post['comments']['data']
                    for comment in comments:
                        comment_message = comment['message']
                        comment_from = comment['from']['name']
                        comment_created_time = comment['created_time']
                        comments_data.append({
                            'comment_message': comment_message,
                            'comment_from': comment_from,
                            'comment_created_time': comment_created_time
                        })
                
                all_data.append({
                    'post_id': post_id,
                    'post_message': post_message,
                    'post_created_time': post_created_time,
                    'comments': comments_data
                })
        else:
            print(f"Error occurred: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    return all_data

def sentiment_analysis_with_transformers(scraped_data):
    # Usar el modelo de Hugging Face preentrenado para análisis de sentimientos
    sentiment_pipeline = pipeline("sentiment-analysis")

    comments = []
    for post in scraped_data:
        for comment in post['comments']:
            comments.append({
                'Post': post['post_message'],
                'Comment': comment['comment_message'],
                'CommentFrom': comment['comment_from'],
                'CreatedTime': comment['comment_created_time']
            })

    df = pd.DataFrame(comments)

    # Limpiar los comentarios
    df['Comment'] = df['Comment'].apply(clean_text)

    # Realizar el análisis de sentimientos
    df['Sentiment'] = df['Comment'].apply(lambda x: sentiment_pipeline(x)[0]['label'])

    return df

def run_scraper_and_analysis():
    # Paso 1: Extraer los datos de Facebook usando la API de Graph
    scraped_data = get_facebook_posts_and_comments()

    # Paso 2: Realizar el análisis de sentimientos en los comentarios extraídos usando Hugging Face
    results = sentiment_analysis_with_transformers(scraped_data)

    # Devolver los resultados como un DataFrame
    return results
