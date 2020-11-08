FROM python:3.8

ARG appversion

LABEL maintainer="Anderson Goulart <global@kokre.io>"
LABEL description="App that monitor PING latency and download/upload internet speed"
LABEL version="$appversion"
RUN apt-get update && apt-get install -y gosu && apt-get clean
WORKDIR /app

COPY . /app
RUN pip3 install pipenv --upgrade && PIPENV_VERBOSITY=-1 pipenv install --dev --pre

CMD [ "gosu", "root", "pipenv", "run", "python", "/app/main.py" ]
