# content_colector/google_sheet_csv.py

import csv
import requests
import io

def get_campaigns_from_csv(csv_url):
    """
    Busca e parseia o CSV publicado no Google Sheets.
    Retorna uma lista de dicionários, cada um representando uma campanha.
    """
    response = requests.get(csv_url)
    if response.status_code != 200:
        raise Exception(f"Erro ao buscar CSV: {response.status_code}")
    
    # Converte o conteúdo em string
    csv_content = response.content.decode('utf-8')
    f = io.StringIO(csv_content)
    reader = csv.DictReader(f)
    campaigns = list(reader)
    return campaigns

if __name__ == "__main__":
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQtUDIgUDNwwEj8GupOqvvokwR4gGzgOWJ7VUA0GK_-lbAwcMdI5bTHb7LYMZeZ11js_QslgLlIBmOK/pub?output=csv"
    campaigns = get_campaigns_from_csv(csv_url)
    for campaign in campaigns:
        print(campaign)
