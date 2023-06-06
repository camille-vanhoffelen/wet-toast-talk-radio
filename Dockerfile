# Build requirements
FROM python:3.10.11-bullseye as builder1

RUN apt-get update && apt-get -y upgrade

WORKDIR /wet-toast-talk-radio

RUN pip install -U pip
RUN pip install pdm

COPY pyproject.toml pdm.lock .

RUN pdm install --prod --no-lock
RUN pdm export --prod --without-hashes -o requirements.txt

# TODO fix
# RUN wget https://downloads.xiph.org/releases/ices/ices-2.0.3.tar.gz

# Build python packages
FROM python:3.10.11-bullseye as builder2

RUN apt-get update && apt-get -y upgrade

RUN useradd --create-home wettoast
WORKDIR /home/wettoast
USER wettoast

RUN pip install -U pip setuptools wheel

COPY --from=builder1 /wet-toast-talk-radio/requirements.txt .
RUN pip install --user -r requirements.txt


# Build prod image
FROM python:3.10.11-slim-bullseye

RUN apt-get update && apt-get -y upgrade
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    libgomp1 

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd --create-home wettoast
WORKDIR /home/wettoast
USER wettoast

COPY --from=builder2 /home/wettoast/.local /home/wettoast/.local
ENV PATH=/home/wettoast/.local/bin:$PATH

# TODO copy only source files instead
COPY . .

# TODO remove
RUN python -m wet_toast_talk_radio.main --help > /dev/null

ENTRYPOINT ["python", "-m", "wet_toast_talk_radio.main"]