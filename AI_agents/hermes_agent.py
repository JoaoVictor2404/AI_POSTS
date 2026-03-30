# AI_agents/hermes_agent.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

def generate_campaign_post(campaign_name, affiliate_link, announcement_text):
    """
    Gera uma postagem promocional para a campanha utilizando o agente Hermes via Gemini.
    """
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise Exception("GEMINI_API_KEY não configurado no ambiente.")
    
    genai.configure(api_key=gemini_api_key)
    
    generation_config = {
        "temperature": 0.6,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-8b",
        generation_config=generation_config,
    )
    
    prompt = f"""
Você é o Hermes, um agente de IA especialista em criar postagens promocionais para campanhas de airdrop na comunidade "Flash Crypto" de até 280 caracteres. 
Sua tarefa é criar uma postagem atraente e informativa com base nos dados da campanha abaixo:

Campanha: {campaign_name}
Link de Afiliado: {affiliate_link}
Texto de Anúncio: {announcement_text}

Crie uma notícia otimizada para SEO com os seguintes elementos:
- Inicie com um parágrafo `<p>` resumo que resuma a notícia e inclua palavras-chave estratégicas para melhorar o ranking nos motores de busca.
- Estruture o conteúdo com subtítulos utilizando `<h2>` e `<h3>` para facilitar a leitura e a indexação, separando diferentes seções informativas.
- Insira meta descrições, atribuições alt para imagens (caso inclua imagens) e links internos/externos pertinentes para enriquecer o SEO da página.
- Desenvolva um texto jornalístico que apresente os fatos, dados relevantes e contexto sobre o tema, mantendo o tom informativo e original, sem copiar literalmente o conteúdo fornecido.
- Evite exageros na repetição das palavras-chave (keyword stuffing) e mantenha a naturalidade e fluidez do texto.

Por favor, gere um JSON válido no seguinte formato:
{{
  "title": "Texto do título (sem tags HTML)",
  "html": "Conteúdo da notícia em HTML, com tags, parágrafos e subtítulos se necessário"
}}
    """
    
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(prompt)
    return response.text.strip()

if __name__ == "__main__":
    # Exemplo de uso
    campaign_name = "Airdrop Flash Crypto"
    affiliate_link = "https://exemplo.com/afiliado123"
    announcement_text = "Participe do nosso airdrop e ganhe tokens exclusivos! Inscreva-se já e aproveite essa oportunidade única."
    post_content = generate_campaign_post(campaign_name, affiliate_link, announcement_text)
    print("Postagem gerada pelo agente Hermes:")
    print(post_content)
