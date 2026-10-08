FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
    fastapi==0.142.2 \
    uvicorn==0.54.0 \
    sqlalchemy \
    python-dotenv \
    passlib \
    bcrypt==4.0.1 \
    python-jose \
    openai \
    slowapi \
    email-validator \
    httpx

RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch && pip install --no-cache-dir chromadb sentence-transformers

COPY app ./app
COPY knowledge ./knowledge

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]