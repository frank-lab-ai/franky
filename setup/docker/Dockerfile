FROM tiangolo/uwsgi-nginx-flask:python3.6

RUN apt-get update
# RUN apt-get install -y python3-pip python3-dev
RUN pip3 install mysqlclient requests pymongo==3.10.1 flask_httpauth flask_cors numpy pandas spacy redis neo4j GPy sklearn matplotlib keras tensorflow py2neo
RUN python3 -m spacy download en

RUN mkdir -p /app/logs/uwsgi
COPY src/ /app