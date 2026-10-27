FROM python:3.12-slim

WORKDIR /gerador

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./ .
EXPOSE 4040

CMD ["python", "gerador/main.py"]
