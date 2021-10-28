FROM python:latest

WORKDIR /app
COPY requirements.txt requirements.txt
COPY . .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "src/main.py"]