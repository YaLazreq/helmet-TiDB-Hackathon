# Utilise une image Python officielle comme base
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir sentence-transformers
		
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY .env .

EXPOSE 8080

CMD ["python", "./mcp/mcp_db/mcp_server.py"]