FROM python:3.12.2

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "main.py"]