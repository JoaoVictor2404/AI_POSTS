# main_hermes.py

from content_colector.google_sheet_csv import get_campaigns_from_csv
from AI_agents.hermes_agent import generate_campaign_post
from post.post_to_x import post_to_x

def main():
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQtUDIgUDNwwEj8GupOqvvokwR4gGzgOWJ7VUA0GK_-lbAwcMdI5bTHb7LYMZeZ11js_QslgLlIBmOK/pub?output=csv"
    
    # Obter as campanhas a partir do CSV
    campaigns = get_campaigns_from_csv(csv_url)
    if not campaigns:
        print("Nenhuma campanha encontrada no CSV.")
        return
    
    # Para este exemplo, escolhemos a primeira campanha da lista.
    campaign = campaigns[0]
    # Utilize as chaves corretas do CSV:
    campaign_name = campaign.get("nome_airdrop") or "Campanha Desconhecida"
    affiliate_link = campaign.get("link_afiliado") or "Link não disponível"
    announcement_text = campaign.get("texto_anuncio") or "Texto não disponível"
    
    print("Dados extraídos da campanha:")
    print("Nome:", campaign_name)
    print("Link:", affiliate_link)
    print("Anúncio:", announcement_text)
    
    # Gerar a postagem com o agente Hermes
    post_content = generate_campaign_post(campaign_name, affiliate_link, announcement_text)
    print("Postagem gerada pelo agente Hermes:")
    print(post_content)
    
    # Publicar a postagem no X (Twitter)
    post_to_x(post_content)

if __name__ == "__main__":
    main()
