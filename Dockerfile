FROM python:3.12-alpine
LABEL authors="jan"

SHELL ["/bin/sh", "-c"]

# Skopiowanie całego katalogu aplikacji
COPY ./app /app

# Skopiowanie pliku requirements.txt
COPY requirements.txt /app

# Instalacja zależności
RUN pip install --no-cache-dir -r /app/requirements.txt

# Ustawienie katalogu roboczego
#WORKDIR /app
#RUN ls -l
# Uruchomienie aplikacji
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["ls", "-l"]




