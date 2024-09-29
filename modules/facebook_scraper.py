import requests
import pandas as pd
import unicodedata
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Token de acceso de la Graph API de Facebook (Asegúrate de que esté actualizado)
access_token = 'EAAGdiBedtwwBOZBbi012VZAkTuh8ro8dJZB4UL5YgxpikWTT2HRNzZBL5BK86cxsnoGQwlpVDzpZCk0QHLpDx1Dou8prKEPUcMQwvRJcVNCB3GOQVjEsvp5ZCz33HWZAR9t2IASWHrXofGy0sPNBZCp1AySyoxI8BtztYDuyqVBI81HbJZBjyy5W7lWZApkSyh'
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
    """
    Realiza la solicitud a la API de Facebook y obtiene los posts junto con sus comentarios.
    """
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

def analyze_sentiment(text):
    """
    Usa VADER para analizar el sentimiento del texto.
    """
    analyzer = SentimentIntensityAnalyzer()
    sentiment_dict = analyzer.polarity_scores(text)
    
    compound = sentiment_dict['compound']

    # Determinar si el sentimiento es positivo, neutro o negativo
    if compound >= 0.05:
        return "Positivo"
    elif compound <= -0.05:
        return "Negativo"
    else:
        return "Neutro"

def run_scraper_and_analysis():
    """
    Realiza el scraping de los comentarios de Facebook y analiza los sentimientos.
    """
    # Extraer los datos de Facebook
    scraped_data = get_facebook_posts_and_comments()

    # Crear una lista para almacenar los resultados
    comments = []
    for post in scraped_data:
        for comment in post['comments']:
            clean_comment = clean_text(comment['comment_message'])
            sentiment = analyze_sentiment(clean_comment)
            comments.append({
                'Post': post['post_message'],
                'Comment': comment['comment_message'],
                'CommentFrom': comment['comment_from'],
                'CreatedTime': comment['comment_created_time'],
                'Sentiment': sentiment  # Resultado del análisis de sentimiento
            })

    # Convertir la lista en un DataFrame de Pandas
    df = pd.DataFrame(comments)

    return df

# Ejemplo de uso
if __name__ == '__main__':
    result_df = run_scraper_and_analysis()
    print(result_df)
