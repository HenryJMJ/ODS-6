import requests

def obtener_noticias_ods6():
    api_key = '92e1fcecc5e54d169fb6c6d68e45aa6b'
    url = f'https://newsapi.org/v2/everything?q=agua+limpia+saneamiento&apiKey={api_key}'
    
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'ok' and data['totalResults'] > 0:
        noticias = []
        for article in data['articles']:
            noticia = {
                'titulo': article['title'],
                'enlace': article['url'],
                'fecha': article['publishedAt'],
                'descripcion': article['description'],
            }
            noticias.append(noticia)
        return noticias
    else:
        print("No se encontraron noticias.")
        return []
