FROM python:3.11-slim

WORKDIR /app

# Kopiere Analyzer-Scripts
COPY grief_detector.py .
COPY grief_web.py .

# Port für Webserver
EXPOSE 8080

# Starte Webserver (Logfile wird als Argument übergeben)
ENTRYPOINT ["python3", "grief_web.py"]
CMD ["--help"]
