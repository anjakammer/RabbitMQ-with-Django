FROM python:3
ENV PYTHONUNBUFFERED 1

RUN mkdir /webapp
WORKDIR /webapp
ADD requirements.txt /webapp/
RUN pip install -r requirements.txt
ADD . /webapp/

EXPOSE 80
CMD echo 'Hello'
