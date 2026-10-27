FROM python3.12-slim

WORKDIR /gerador

COPY /opt/projeto/gerador/requirements.txt .
RUN pip install -r requirements.txt

COPY /opt/projeto/gerador/ .
EXPOSE 4040

CMD ["python", "gerador/main.py"]
