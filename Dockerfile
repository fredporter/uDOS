FROM python:3.11-alpine

WORKDIR /uDOS

RUN apk add --no-cache bash curl git tini nano

COPY . /uDOS
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /uKnowledge /uMemory /config /uMemory/logs/system

RUN chmod +x scripts/launch-uDOS.sh

CMD ["bash", "scripts/launch-uDOS.sh"]
