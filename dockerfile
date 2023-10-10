FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN apt-get clean \
    && apt-get -y update

RUN apt-get -y install python3-dev \
    && apt-get -y install build-essential \
    && apt-get -y install libpq-dev

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uwsgi", "--ini", "uwsgi.ini"]