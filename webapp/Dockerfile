FROM python:3
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y wget

RUN wget https://storage.googleapis.com/golang/go1.8.3.linux-amd64.tar.gz
RUN tar -xvf go1.8.3.linux-amd64.tar.gz
RUN mv go /usr/local

RUN mkdir /webapp

# Golang config
ENV GOROOT      /usr/local/go
ENV GOPATH     /webapp
ENV PATH       $GOPATH/bin:$GOROOT/bin:$PATH

# ipfs config
ENV IPFS_PATH /data/ipfs
RUN go get -u github.com/ipfs/ipfs-update
RUN ipfs-update install latest
VOLUME $IPFS_PATH

WORKDIR /webapp
ADD requirements.txt /webapp/
RUN pip install -r requirements.txt
ADD . /webapp/

EXPOSE 80

# honcho - starts ipdf daemon and django server
RUN pip install honcho
ADD Procfile /Procfile
WORKDIR /
CMD honcho start
