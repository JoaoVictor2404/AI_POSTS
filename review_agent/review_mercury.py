# review_agent/review_mercury.py

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

def review_mercury_content(content):
    """
    Recebe um conteúdo (por exemplo, em HTML) e utiliza a API Gemini para revisá-lo.
    O agente revisor corrige erros gramaticais, melhora a estrutura e otimiza o texto para SEO.
    
    Retorna o conteúdo revisado (texto em formato puro, sem comentários adicionais).
    """
    load_dotenv()
    
    # Configurar a API Gemini com a chave de API
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise Exception("GEMINI_API_KEY não configurado no ambiente.")
    genai.configure(api_key=gemini_api_key)
    
    # Configuração do modelo para revisão
    generation_config = {
        "temperature": 0.6,
        "top_p": 0.9,
        "max_output_tokens": 1024,
        "response_mime_type": "text/plain",
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
    )
    
    # Montar o prompt para revisão do conteúdo
    prompt = f"""
Você é um agente revisor de conteúdo.
Revise o conteúdo a seguir, se tiver algo que incite algum crime ou preconceito retorne "conteúdo excluido", se não apenas retorne o conteúdo que recebeu sem alteração nennhuma. 
Não inclua comentários extras, retorne apenas o conteúdo no mesmo formato recebido.:
---
Conteúdo a revisar:
{content}
---
    """
    
    # Iniciar a sessão de chat com o modelo Gemini e enviar o prompt
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(prompt)
    reviewed_content = response.text.strip()
    
    return reviewed_content

if __name__ == "__main__":
    # Exemplo de uso
    sample_content = (
        "<p>Este é um exemplo de conteudo para ser revisado. "
        "Possui erros, má estrutura e precisa ser aprimorado para SEO.</p>"
    )
    revised = review_mercury_content(sample_content)
    print("Conteúdo revisado:")
    print(revised)
