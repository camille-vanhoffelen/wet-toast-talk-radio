FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu20.04

# Needed to avoid geography questions on apt-get install
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    libgomp1 \
    libshout3-dev \
    curl \
    git \
    vim

RUN apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get install -y python3.10-dev

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

ENTRYPOINT ["bash"]