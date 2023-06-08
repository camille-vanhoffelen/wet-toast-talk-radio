# Install python dependencies
FROM python:3.10.11-bullseye as builder

RUN apt-get update && apt-get -y upgrade

RUN useradd --create-home wettoast
WORKDIR /home/wettoast
USER wettoast

RUN pip install --no-warn-script-location -U pip setuptools wheel

COPY ./requirements.txt .
RUN pip install --no-warn-script-location --user -r requirements.txt

RUN wget https://downloads.xiph.org/releases/ices/ices-2.0.3.tar.gz

# GPU prod image
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu20.04 AS prod-gpu

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    libgomp1

RUN apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install -y python3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd --create-home wettoast
WORKDIR /home/wettoast
USER wettoast

COPY --from=builder /home/wettoast/.local /home/wettoast/.local
ENV PATH=/home/wettoast/.local/bin:$PATH

COPY ices ./ices
COPY wet_toast_talk_radio ./wet_toast_talk_radio

# TODO remove this test when we are confident the dockers work everywhere
RUN python3.10 -m wet_toast_talk_radio.main --help > /dev/null

ENTRYPOINT ["python3.10", "-m", "wet_toast_talk_radio.main"]

# Prod image
FROM python:3.10.11-slim-bullseye AS prod

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    libgomp1

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd --create-home wettoast
WORKDIR /home/wettoast
USER wettoast

COPY --from=builder /home/wettoast/.local /home/wettoast/.local
ENV PATH=/home/wettoast/.local/bin:$PATH

COPY ices ./ices
COPY wet_toast_talk_radio ./wet_toast_talk_radio

# TODO remove this test when we are confident the dockers work everywhere
RUN python -m wet_toast_talk_radio.main --help > /dev/null

ENTRYPOINT ["python", "-m", "wet_toast_talk_radio.main"]