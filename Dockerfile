FROM python:3.10 as builder

RUN pip install -U pip setuptools wheel
RUN pip install pdm

WORKDIR /wet-toast-talk-radio
RUN wget https://downloads.xiph.org/releases/ices/ices-2.0.3.tar.gz

COPY . .
RUN pdm install --prod --no-lock

FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    libgomp1 

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/wet-toast-talk-radio/.venv/bin:$PATH"

WORKDIR /wet-toast-talk-radio
COPY --from=builder /wet-toast-talk-radio .
RUN python -m wet_toast_talk_radio.main --help > /dev/null

ENTRYPOINT ["python", "-m", "wet_toast_talk_radio.main"]