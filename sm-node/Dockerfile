FROM python:3.8-slim-buster

ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD . .

CMD ["python3", "daemon.py"]
