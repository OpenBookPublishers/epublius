FROM python:3.8-slim-buster

WORKDIR /ebook_automation

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/ ./

ENV OUTDIR=/ebook_automation/output

ENTRYPOINT ["python3"]

CMD ["./thoth_wrapper.py", "--help"]
