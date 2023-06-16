# Install python dependencies
FROM python:3.10.11-bullseye as builder

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
    libshout3-dev

RUN useradd --create-home wettoast
WORKDIR /home/wettoast
USER wettoast

RUN pip install --no-warn-script-location -U pip setuptools wheel

COPY ./requirements.txt .
RUN pip install --no-warn-script-location --user -r requirements.txt


# GPU prod image
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04 AS prod-gpu

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

# overwrite pytorch w/ nightly GPU build
RUN python3.10 -m pip install --pre torch torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121

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

COPY --from=builder /home/wettoast/.local /home/wettoast/.local
ENV PATH=/home/wettoast/.local/bin:$PATH

COPY wet_toast_talk_radio ./wet_toast_talk_radio

ENTRYPOINT ["python", "-m", "wet_toast_talk_radio.main"]
