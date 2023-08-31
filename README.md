![Wet Toast Talk Radio logo](resources/wttr-logo-thin.jpg)

# Wet Toast Talk Radio


[![Radio Listen](https://img.shields.io/badge/%F0%9F%8D%9E_radio-Listen-F09F39?style=for-the-badge)](https://www.wettoast.ai/)
[![Twitch Watch](https://img.shields.io/badge/Twitch-Watch-9146FF?style=for-the-badge&logo=twitch)](https://www.twitch.tv/wettoasttalkradio)

_Fake talk. Fake issues. Real giggles._

Generating content for Wet Toast Talk Radio, a 24/7 non-stop internet parody radio inspired by GTA. 

We don’t do reruns - all shows are generated daily. We use ChatGPT + a lot of prompt engineering and randomization for the writing of the scripts, and the amazing transformer + diffusion models of [tortoise-tts](https://github.com/neonbjb/tortoise-tts) for speech generation.

Checkout our [website](https://www.wettoast.ai/)!

# ToC

* [🚀 Getting Started](#-getting-started)
* [🍞 Usage](#-usage)
* [⚙️ Development](#-development)
* [🚢 Deployment](#-deployment)
* [😎 Credits](#-credits)
* [🤝 License](#-license)


## 🚀 Getting Started

### Prerequisites

- python >= 3.10
- [ffmpeg](https://github.com/jiaaro/pydub#getting-ffmpeg-set-up) `brew install ffmpeg`
- [libshout](https://icecast.org/download/) `brew install libshout`

### Install from Source

Install the package with pip:

```commandline
pip install -r requirements.txt
pip install -e .
```

or with your preferred virtual environment manager (_this project uses [pdm](https://pdm.fming.dev/) for dependency management_).

### Configuration

Add your OpenAI API key in a `config.yml` file in the project dir:

```yaml
scriptwriter:
  llm:
    openai_api_key: YOUR_OPENAI_API_KEY
```


## 🍞 Usage

⚠️ This CLI is designed as a demo of WTTR's generative capabilities. The full production services require to be deployed as part of the stack in the [aws](aws) directory.

### ✍️ Script Generation

To write a single script show:

```commandline
python -m wet_toast_talk_radio.main scriptwriter SHOW_NAME [--output-dir]
```

Currently available shows:

Show Name | Host | Description
---|---|---
`the-great-debate` | Julie | The show where you tune in to take sides
`modern-mindfulness` | Orion | Combining mindfulness and exposure therapy to let go of modern anxiety
`the-expert-zone` | Nick | The show where we ask the experts the difficult questions
`prolove` | Zara | The dating advice show where we love listening to you
`advert` | Ian | Advertisements from our beloved sponsors

For example, to generate an advertisement script in the folder output:

```commandline
python -m wet_toast_talk_radio.main scriptwriter advert --output-dir output
```

### 🗣 Audio Generation

TODO warning about GPU, plus CUDA dependencies. See XXXX to install dependencies.

### 💽 Audio Transcoding

### 🎶 Playlist Creation

### 📻 Radio Streaming

## ⚙️ Development

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

### Requirements Building

`create-requirements.sh`

### Testing

The [test](./tests/) folder containes integration tests that need the `docker-compose up` cmd to run. These tests are skipped by default but can be enabled with the following flag: 

```bash
pdm run pytest --integration
```

### Code Standards

We use [black](https://github.com/psf/black) as our code formattter.

We use [ruff](https://beta.ruff.rs/docs/) as our linter.

We use [pytest](https://docs.pytest.org/en/6.2.x/) as our testing framework.

Commits should follow the following convention:  `refactor|feat|fix|docs|breaking|misc|chore|test: description`


## Deployment

[./aws/README.md](./aws/README.md)


## Credits

## License