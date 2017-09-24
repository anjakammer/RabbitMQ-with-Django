FROM python:3
ENV PYTHONUNBUFFERED 1

RUN mkdir /ocr
WORKDIR /ocr
ADD requirements.txt /ocr/
RUN pip install -r requirements.txt
ADD . /ocr/