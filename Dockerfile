FROM python:3-slim-buster

WORKDIR /ebook_automation

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/ ./

ENV OUTDIR=/ebook_automation/output

CMD bash run epub_file
