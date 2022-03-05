
FROM python:3.9.7-bullseye

LABEL GSyA Research Group <https://gsya.esi.uclm.es/>

RUN apt-get update && apt-get install -y python3-pip

RUN pip3 install \
    requests \
    typer

WORKDIR /usr/local/src/
COPY . /usr/local/src/

ENTRYPOINT ["python", "graph_model_to_neo4j.py"]