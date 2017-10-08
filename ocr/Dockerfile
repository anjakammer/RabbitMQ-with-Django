FROM dbmobilelife/docker-python-opencv-tesseract
ENV PYTHONUNBUFFERED 1

RUN locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

RUN apt-get update && apt-get install -y \
        software-properties-common \
        swig \
        python3-dev \
        python3-setuptools \
        python3-pip \
        tesseract-ocr-deu \
        tesseract-ocr-eng

RUN mkdir /ocr
WORKDIR /ocr
ADD requirements.txt /ocr/
RUN pip3 install -r requirements.txt
ADD . /ocr/