# create_image/mercury_image.py

import os
import mimetypes
from google import genai
from google.genai import types
from dotenv import load_dotenv

def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)

def generate_image_from_title(title, file_name_prefix="mercury_image"):
    """
    Gera uma imagem usando o modelo Gemini a partir do título fornecido.
    O prompt é montado para solicitar uma imagem que ilustre a notícia.
    
    Retorna o nome do arquivo salvo (ex.: "mercury_image.png").
    """
    load_dotenv()
    
    # Inicializa o cliente com a GEMINI_API_KEY
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY")
    )
    
    # Modelo para geração de imagens
    model = "gemini-2.0-flash-exp-image-generation"
    
    # Cria o prompt: peça uma imagem que ilustre a notícia com base no título
    prompt_text = f"Crie uma imagem que ilustre a seguinte notícia: {title}"
    
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt_text)]
        )
    ]
    
    generate_config = types.GenerateContentConfig(
        temperature=1.3,
        response_modalities=["image", "text"],
        response_mime_type="text/plain"
    )
    
    # Processa a resposta em streaming
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_config,
    ):
        if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
            continue
        part = chunk.candidates[0].content.parts[0]
        if part.inline_data:
            file_ext = mimetypes.guess_extension(part.inline_data.mime_type)
            file_name = f"{file_name_prefix}{file_ext}"
            save_binary_file(file_name, part.inline_data.data)
            print(f"Imagem gerada e salva como: {file_name}")
            return file_name
        else:
            print("Resposta textual recebida:", chunk.text)
    return None

if __name__ == "__main__":
    # Exemplo de uso:
    sample_title = "Banco Central Aumenta Aposta em Criptomoedas"
    generate_image_from_title(sample_title)
