import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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

def analyze_sentiment_from_csv(file_path):
    """
    Lee un archivo CSV y analiza los sentimientos de la columna 'postText'.
    """
    # Leer el archivo CSV
    df = pd.read_csv(file_path)

    # Asegúrate de que la columna 'postText' existe
    if 'postText' not in df.columns:
        raise ValueError("El archivo CSV debe contener una columna llamada 'postText'.")

    # Analizar sentimientos
    df['Sentiment'] = df['postText'].apply(analyze_sentiment)

    return df
