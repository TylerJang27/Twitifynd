FROM ubuntu:20.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev postgresql-client

# TODO: ADD PIP REQUIREMENTS TO requirements.txt
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /code
COPY . /code

ENTRYPOINT ["bash","./init.sh"]
