# Use uma imagem oficial Python leve
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação
COPY . .

# Expõe a porta que o Flask irá escutar
EXPOSE 5000


# Comando padrão para inicializar o serviço
CMD ["python", "scheduler.py"]
