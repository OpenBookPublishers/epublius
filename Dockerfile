FROM python:2-slim-buster

WORKDIR /ebook_automation

RUN apt-get update && \
    apt-get install -y zip
RUN rm -rf /var/cache/apt/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/ ./

ENV OUTDIR=/ebook_automation/output

CMD bash run epub_file
