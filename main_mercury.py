# main_mercury.py

from AI_agents.mercury_agent import generate_mercury_post
from review_agent.review_mercury import review_mercury_content
from create_image.mercury_image import generate_image_from_title
from post.post_blog import create_blog_post, upload_feature_image
import json

def main():
    reddit_file_path = "data/api_connector_reddit_content.json"
    
    # Gerar o conteúdo pelo agente Mercury
    mercury_content = generate_mercury_post(reddit_file_path)
    print("Conteúdo gerado pelo agente Mercury (antes da revisão):")
    print(json.dumps(mercury_content, indent=4, ensure_ascii=False))
    
    # Revisar o conteúdo utilizando o agente revisor
    # Aqui, revisamos o HTML (corpo da notícia) para corrigir e otimizar
    reviewed_html = review_mercury_content(mercury_content.get("html", ""))
    mercury_content["html"] = reviewed_html
    print("Conteúdo revisado pelo agente Mercury:")
    print(json.dumps(mercury_content, indent=4, ensure_ascii=False))
    
    # Gerar a imagem com base no título (pode ser o mesmo título, já que geralmente ele não necessita de revisão)
    title = mercury_content.get("title", "Notícia do Mercury")
    local_image_path = generate_image_from_title(title)
    print(f"Imagem gerada: {local_image_path}")
    
    # Fazer o upload da imagem para o Ghost para obter a URL pública
    feature_image_url = None
    if local_image_path:
        feature_image_url = upload_feature_image(local_image_path)
        print(f"URL da imagem no Ghost: {feature_image_url}")
    
    # Publicar a postagem no Ghost, incluindo a feature_image
    response = create_blog_post(mercury_content, feature_image_url=feature_image_url)
    if response.status_code in [200, 201]:
        print("Postagem criada com sucesso no Ghost!")
    else:
        print("Erro ao criar a postagem no Ghost:")
        print(response.text)

if __name__ == "__main__":
    main()
