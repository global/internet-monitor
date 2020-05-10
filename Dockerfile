FROM python:3

RUN apt-get update && apt-get install -y gosu

WORKDIR /app

COPY requirements.txt /app
COPY main.py /app
COPY monitor.yml /app

RUN pip3 install -r requirements.txt

CMD [ "gosu", "root", "python", "/app/main.py" ]