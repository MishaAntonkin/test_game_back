FROM python:3.8

RUN apt-get install -y git
WORKDIR /work
ADD . /work

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .
