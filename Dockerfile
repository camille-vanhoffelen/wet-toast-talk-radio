# Install CPU python dependencies
FROM python:3.10.11-bullseye as builder-cpu

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
    libshout3-dev

RUN useradd --create-home wettoast
WORKDIR /home/wettoast
USER wettoast

RUN pip install --no-warn-script-location -U pip setuptools wheel

COPY ./requirements.txt .

# hack to pin pytorch stable cpu build
RUN pip install --no-warn-script-location --user --pre -r requirements.txt --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple

# Install GPU python dependencies
FROM python:3.10.11-bullseye as builder-gpu

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
    libshout3-dev

RUN useradd --create-home wettoast
WORKDIR /home/wettoast
USER wettoast

RUN pip install --no-warn-script-location -U pip setuptools wheel

COPY ./requirements.txt .

# hack to pin pytorch stable CUDA 11.7 build
RUN pip install --no-warn-script-location --user --pre -r requirements.txt --index-url https://download.pytorch.org/whl/cu117 --extra-index-url https://pypi.org/simple

# GPU prod image
FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu20.04 AS prod-gpu

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    libgomp1 \
    libshout3-dev

RUN apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install -y python3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd --create-home wettoast
WORKDIR /home/wettoast
USER wettoast

COPY --from=builder-gpu /home/wettoast/.local /home/wettoast/.local
ENV PATH=/home/wettoast/.local/bin:$PATH

COPY wet_toast_talk_radio ./wet_toast_talk_radio

ENTRYPOINT ["python3.10", "-m", "wet_toast_talk_radio.main"]

# Prod image
FROM python:3.10.11-slim-bullseye AS prod

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    libgomp1 \
    libshout3-dev

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd --create-home wettoast
WORKDIR /home/wettoast
USER wettoast

COPY --from=builder-cpu /home/wettoast/.local /home/wettoast/.local
ENV PATH=/home/wettoast/.local/bin:$PATH

COPY wet_toast_talk_radio ./wet_toast_talk_radio

ENTRYPOINT ["python", "-m", "wet_toast_talk_radio.main"]
