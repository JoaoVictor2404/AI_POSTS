# post/post_blog.py
import os, yaml, pathlib
import os
import time
import jwt
import requests
import json

CONFIG_NAME = os.getenv("CONFIG_FILE", "flash_crypto.yml")
CONFIG_PATH = pathlib.Path("configs") / CONFIG_NAME

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)


def generate_jwt(secret, key_id):
    """
    Gera o token JWT para autenticação na Admin API do Ghost.
    O token é válido por 5 minutos.
    """
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 5 * 60,  # token válido por 5 minutos
        "aud": "/v3/admin/"
    }
    headers = {
        "alg": "HS256",
        "typ": "JWT",
        "kid": key_id
    }
    secret_bytes = bytes.fromhex(secret)
    token = jwt.encode(payload, secret_bytes, algorithm="HS256", headers=headers)
    return token

def post_blog_post(api_url, token, post_data):
    """
    Realiza a requisição POST para criar uma nova postagem no Ghost.
    """
    headers = {
        "Authorization": f"Ghost {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(api_url, headers=headers, json=post_data)
    return response

def upload_feature_image(image_path):
    """
    Faz o upload da imagem para o Ghost e retorna a URL da imagem.
    """
    ghost_domain = os.getenv("GHOST_DOMAIN", "airdrop.ghost.io")  # Adicione a variável GHOST_DOMAIN no .env se desejar
    api_version = "v3"
    upload_url = f"https://{ghost_domain}/ghost/api/{api_version}/admin/images/upload/"
    
    # Gerar token JWT para autenticação
    secret = os.getenv("GHOST_SECRET")
    key_id = os.getenv("GHOST_KEY_ID")
    token = generate_jwt(secret, key_id)
    
    headers = {
        "Authorization": f"Ghost {token}"
    }
    
    # Abra o arquivo de imagem e envie como multipart/form-data
    with open(image_path, 'rb') as img:
        # Configure o nome e o mime da imagem (ajuste se necessário)
        files = {
            "file": (os.path.basename(image_path), img, "image/png")
        }
        response = requests.post(upload_url, headers=headers, files=files, verify=False)
        
    if response.status_code in [200, 201]:
        # O response.json() normalmente contém o objeto image com a URL
        data = response.json()
        image_url = data.get("images", [{}])[0].get("url")
        return image_url
    else:
        print("Erro no upload da imagem:")
        print(response.text)
        return None

def create_blog_post(mercury_content, feature_image_url=None):
    """
    Recebe o conteúdo gerado pelo Mercury (um dict com 'title' e 'html')
    e cria o post_data para o Ghost, incluindo a feature_image, se disponível.
    """
    ghost_domain = os.getenv("GHOST_DOMAIN", "airdrop.ghost.io")  # Use uma variável de ambiente se desejar
    api_version = "v3"
    api_url = f"https://{ghost_domain}/ghost/api/{api_version}/admin/posts/?source=html"
    
    secret = os.getenv("GHOST_SECRET")
    key_id = os.getenv("GHOST_KEY_ID")
    token = generate_jwt(secret, key_id)
    
    post_data = {
        "posts": [
            {
                "tags": CFG["ghost_tags"],
                "title": mercury_content.get("title", "Notícia do Mercury"),
                "html": mercury_content.get("html", "<p>Conteúdo indisponível.</p>"),
                "status": CFG["publish_status"],
                "feature_image": feature_image_url  # URL da imagem que foi feita o upload
            }
        ]
    }
    
    response = post_blog_post(api_url, token, post_data)
    return response

def main():
    # Função de teste, se executar este arquivo sozinho
    test_content = {
        "title": "Exemplo de Título Gerado",
        "html": "<p>Este é um exemplo de conteúdo HTML gerado pelo Mercury.</p>"
    }
    # Para teste, defina o caminho da imagem manualmente
    test_image = "mercury_image.png"
    image_url = upload_feature_image(test_image)
    response = create_blog_post(test_content, feature_image_url=image_url)
    if response.status_code in [200, 201]:
        print("Postagem criada com sucesso!")
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))
    else:
        print("Erro ao criar a postagem.")
        print(f"Status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()
