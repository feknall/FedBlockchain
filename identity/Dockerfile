#FROM python:3.9.12
FROM bcgovimages/von-image:py36-1.15-1

COPY . /project
WORKDIR /project

ENV PYTHONPATH=${PYTHONPATH}:/project
ENV LEDGER_URL=http://localhost:9000
ENV GENESIS_FILE=/project/von-network/genesis/genesis.txt

#RUN add-apt-repository "deb https://repo.sovrin.org/sdk/deb bullseye stable"
RUN #apt-get update && apt-get install -y libindy

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r /project/requirements.txt

