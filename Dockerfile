# Use Python 3.11 slim como base
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias para pandas e openpyxl
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de requisitos
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY dashboard_flask.py .
COPY ["LICENCIAMENTO MICROSOFT (1).xlsx", "."]
COPY static/ ./static/

# Expor porta 5000
EXPOSE 5000

# Definir variáveis de ambiente
ENV FLASK_APP=dashboard_flask.py
ENV PYTHONUNBUFFERED=1

# Comando para iniciar a aplicação
CMD ["python", "dashboard_flask.py"]
