FROM python:3

WORKDIR /app

COPY ./requirements.txt /app
RUN pip3 install -r requirements.txt

COPY main.py /app
ENV FLASK_APP='/app/main.py'

CMD [ "flask", "run", "--host=0.0.0.0" ]
