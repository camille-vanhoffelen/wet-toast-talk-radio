![Wet Toast Talk Radio logo](resources/wttr-logo-thin.png)

# :bread: Wet Toast Talk Radio

Generating content for Wet Toast Talk Radio

## Devolpment

### Prerequisite

- [pdm](https://pdm.fming.dev/latest/)
- python >= 3.10
- [ffmpeg](https://github.com/jiaaro/pydub#getting-ffmpeg-set-up) `brew install ffmpeg`

### Config

You will likely want to create a config.yaml with these contents:

```yaml
media_store:
  virtual: true
```

### Running

```bash
pdm run main.py --help
```

### Docker-compose

```bash
docker-compose up
```

#### S3

A localstack s3 bucket named `wet-toast-talk-radio` is located at [http://localhost:4566](http://localhost:4566).

You can access it from the cli like this:

```bash
aws s3 --endpoint-url=http://localhost:4566 cp ./wet_toast_talk_radio/media_store/virtual/data s3://wet-toast-talk-radio/raw --recursive
aws s3 --endpoint-url=http://localhost:4566 ls s3://wet-toast-talk-radio/raw/
aws s3 --endpoint-url=http://localhost:4566 ls s3://wet-toast-talk-radio/transcoded/
aws s3 --endpoint-url=http://localhost:4566 rm s3://wet-toast-talk-radio/transcoded/ --recursive
```

#### Icecast

A Icecast and Ices service will start on [http://localhost:8000/](http://localhost:8000/)

### Testing

The [test](./tests/) folder containes integration tests that need the `docker-compose up` cmd to run. These tests are skipped by default but can be enabled with the following flag: 

```bash
pdm run pytest --intergration
```


## Deployment

[./aws/README.md](./aws/README.md)

## Contributing

- Commits should follow the following convention:  `refactor|feat|fix|docs|breaking|misc|chore|test: description`


## Code Standards

We use [black](https://github.com/psf/black) as our code formattter.

We use [ruff](https://beta.ruff.rs/docs/) as our linter.

We use [pytest](https://docs.pytest.org/en/6.2.x/) as our testing framework.

