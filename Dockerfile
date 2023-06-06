FROM python:3.10.11-bullseye as builder

RUN apt-get update && apt-get -y upgrade

RUN useradd --create-home wettoast
WORKDIR /home/wettoast
USER wettoast

RUN pip install -U pip setuptools wheel

COPY ./requirements.txt .
RUN pip install --user -r requirements.txt

RUN wget https://downloads.xiph.org/releases/ices/ices-2.0.3.tar.gz

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

COPY --from=builder /home/wettoast/.local /home/wettoast/.local
ENV PATH=/home/wettoast/.local/bin:$PATH

COPY . .

ENTRYPOINT ["python", "-m", "wet_toast_talk_radio.main"]