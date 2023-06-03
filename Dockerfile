FROM python:3.10 AS builder

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install -U pip setuptools wheel
RUN pip install pdm

WORKDIR /wet-toast-talk-radio

COPY pyproject.toml pdm.lock .
RUN pdm install --prod --no-lock

COPY . .

FROM python:3.10-slim

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PATH="/wet-toast-talk-radio/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y libgomp1

WORKDIR /wet-toast-talk-radio

COPY --from=builder /wet-toast-talk-radio .

ENTRYPOINT ["python", "-m", "main"]