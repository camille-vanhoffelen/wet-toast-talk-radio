![Wet Toast Talk Radio logo](resources/wttr-logo-thin.png)

# :bread: Wet Toast Talk Radio

Generating content for Wet Toast Talk Radio

## Devolpment

### Prerequisite

- [pdm](https://pdm.fming.dev/latest/)
- python >= 3.10
- [ffmpeg](https://github.com/jiaaro/pydub#getting-ffmpeg-set-up) `brew install ffmpeg`
- [libshout] `brew install libshout`

### Config

You will likely want to create a config.yml with these contents:

```yaml
# emergency_alert_system:
#   web_hook_url: sm:/wet-toast-talk-show/emergency-alert-system/slack-web-hook-url
# radio_operator:
#   web_hook_url: sm:/wet-toast-talk-show/radio-operator/slack-web-hook-url
message_queue:
  # virtual: true
  sqs:
    local: true
media_store:
  # virtual: true
  s3:
    local: true
    bucket_name: "media-store"
audio_generator:
  # If HF Hub cache empty, download models from S3 instead of the internet
  use_s3_model_cache: true
scriptwriter:
  llm:
    # virtual: true
    # fake_responses: ["Yeah sure", "Nah bro"]
    openai_api_key: sm:/wet-toast-talk-radio/scriptwriter/openai-api-key
  
disc_jockey:
  media_transcoder:
    clean_tmp_dir: false
  shout_client:
    password: "hackme"
    # Uncomment to stream to voscast directly
    # password: sm:/wet-toast-talk-radio/voscast-password
    # hostname: s3.voscast.com
    # port: 11052
    # autodj_key: sm:/wet-toast-talk-radio/voscast-autodj-key
```

### Running

```bash
pdm run python -m wet_toast_talk_radio.main --help
```

### Docker-compose

```bash
docker-compose up
```

#### S3

A localstack s3 bucket named `wet-toast-talk-radio` is located at [http://localhost:4566](http://localhost:4566).

You can access it from the cli like this:

```bash
aws --endpoint-url=http://localhost:4566 s3 cp ./wet_toast_talk_radio/media_store/virtual/data s3://wet-toast-talk-radio/raw --recursive
aws --endpoint-url=http://localhost:4566 s3 ls s3://media-store/raw/
aws --endpoint-url=http://localhost:4566 s3 ls s3://media-store/transcoded/
aws --endpoint-url=http://localhost:4566 s3 rm s3://media-store/transcoded/ --recursive
```

#### SQS

A localstack sqs MQ is located at [http://localhost:4566](http://localhost:4566).

You can access it from the cli like this:

```bash
aws --endpoint-url=http://localhost:4566 sqs list-queues
```

#### Icecast

A Icecast and Ices service will start on [http://localhost:8000/](http://localhost:8000/)

### Testing

The [test](./tests/) folder containes integration tests that need the `docker-compose up` cmd to run. These tests are skipped by default but can be enabled with the following flag: 

```bash
pdm run pytest --integration
```


## Deployment

[./aws/README.md](./aws/README.md)

## Contributing

- Commits should follow the following convention:  `refactor|feat|fix|docs|breaking|misc|chore|test: description`


## Code Standards

We use [black](https://github.com/psf/black) as our code formattter.

We use [ruff](https://beta.ruff.rs/docs/) as our linter.

We use [pytest](https://docs.pytest.org/en/6.2.x/) as our testing framework.

