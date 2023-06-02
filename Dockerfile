FROM python:3.10 AS builder

RUN pip install -U pip setuptools wheel
RUN pip install pdm

WORKDIR /wet_toast_talk_radio
COPY . .
RUN mkdir __pypackages__ && pdm sync --prod --no-editable

FROM python:3.10

# retrieve packages from build stage
ENV PYTHONPATH=/wet_toast_talk_radio/pkgs
COPY --from=builder /wet_toast_talk_radio/__pypackages__/3.10/lib /wet_toast_talk_radio/pkgs

ENTRYPOINT ["python", "-m", "wet_toast_talk_radio"]