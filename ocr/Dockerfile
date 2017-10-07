FROM dbmobilelife/docker-python-opencv-tesseract
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
        software-properties-common \
        python3-dev \
        python3-setuptools \
        python3-pip

RUN mkdir /ocr
WORKDIR /ocr
ADD requirements.txt /ocr/
RUN pip3 install -r requirements.txt
ADD . /ocr/