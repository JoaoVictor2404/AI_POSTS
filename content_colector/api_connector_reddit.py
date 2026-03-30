# content_colector/api_connector_reddit.py

import os, pathlib, yaml
import json
import praw
from dotenv import load_dotenv

CONFIG_NAME = os.getenv("CONFIG_FILE", "flash_crypto.yml")
CFG_PATH = pathlib.Path("configs") / CONFIG_NAME

with open(CFG_PATH, "r", encoding="utf-8") as fh:
    CFG = yaml.safe_load(fh)
CONFIG_SUBREDDIT = CFG['subreddits']

def collect_reddit_posts():
    """
    Conecta ao Reddit, coleta os posts dos subreddits definidos e salva em um arquivo JSON.
    """
    load_dotenv()
    
    # Configurar a conexão com o Reddit
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent='NexusTrendCollector by /u/SeuNomeDeUsuario',
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD")
    )
    
    # Lista de subreddits a serem consultados
    subreddits = CONFIG_SUBREDDIT
    
    # Lista para armazenar os posts coletados
    posts_reddit = []
    
    # Função para coletar posts de um determinado subreddit
    def coletar_posts(subreddit_name):
        print(f"Coletando posts do subreddit: {subreddit_name}")
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.hot(limit=50):
            post_info = {
                'title': post.title,
                'selftext': post.selftext,
                'score': post.score,
                'url': post.url,
                'created_utc': post.created_utc,
                'subreddit': subreddit_name
            }
            posts_reddit.append(post_info)
    
    # Iterar sobre os subreddits e coletar os posts
    for sub in subreddits:
        try:
            coletar_posts(sub)
        except Exception as e:
            print(f"Erro ao coletar posts de {sub}: {e}")
    
    print(f"Total de posts coletados: {len(posts_reddit)}")
    
    # Salvar os posts coletados em um arquivo JSON dentro da pasta 'data'
    output_file = 'data/api_connector_reddit_content.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(posts_reddit, f, ensure_ascii=False, indent=4)
    
    print(f"Conteúdo do Reddit coletado e salvo em '{output_file}'.")

if __name__ == "__main__":
    collect_reddit_posts()
