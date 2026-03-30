# post/post_to_x.py

import os
import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv

def post_to_x(content):
    """
    Posta o conteúdo gerado no X (Twitter) utilizando a API v2 via requests com OAuth 1.0a.
    """
    load_dotenv()
    
    # Obter as credenciais do X (Twitter) das variáveis de ambiente
    consumer_key = os.getenv("X_API_KEY")
    consumer_secret = os.getenv("X_API_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")
    
    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        raise Exception("Credenciais do X não configuradas nas variáveis de ambiente.")
    
    # Configurar a autenticação OAuth1
    auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)
    
    url = "https://api.twitter.com/2/tweets"
    
    payload = {
        "text": content
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers, auth=auth)
    
    if response.status_code in [200, 201]:
        print("Postagem realizada com sucesso no X:")
        print(response.text)
    else:
        print("Erro ao postar no X:")
        print(response.text)

if __name__ == "__main__":
    sample_content = (
        "Confira nossa nova notícia do universo cripto gerada pelo Mercury! "
        "Fique por dentro das últimas novidades."
    )
    post_to_x(sample_content)
