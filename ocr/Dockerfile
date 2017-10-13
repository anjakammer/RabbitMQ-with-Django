FROM dbmobilelife/docker-python-opencv-tesseract
ENV PYTHONUNBUFFERED 1

RUN locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

RUN apt-get update && apt-get install -y \
        software-properties-common \
        wget \
        git \
        swig \
        python3-dev \
        python3-setuptools \
        python3-pip \
        tesseract-ocr-deu \
        tesseract-ocr-eng

RUN wget https://storage.googleapis.com/golang/go1.8.3.linux-amd64.tar.gz
RUN tar -xvf go1.8.3.linux-amd64.tar.gz
RUN mv go /usr/local

RUN mkdir /ocr

# Golang config
ENV GOROOT      /usr/local/go
ENV GOPATH     /webapp
ENV PATH       $GOPATH/bin:$GOROOT/bin:$PATH

# ipfs config
ENV IPFS_PATH /data/ipfs
RUN go get -u github.com/ipfs/ipfs-update
RUN ipfs-update install latest
VOLUME $IPFS_PATH

WORKDIR /ocr
ADD requirements.txt /ocr/
RUN pip3 install -r requirements.txt
ADD . /ocr/

# honcho - starts ipdf daemon and django server
RUN pip3 install honcho
ADD Procfile /Procfile
WORKDIR /
CMD honcho start
