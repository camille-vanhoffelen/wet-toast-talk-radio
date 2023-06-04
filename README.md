![Wet Toast Talk Radio logo](resources/wttr-logo-thin.png)

# :bread: Wet Toast Talk Radio

Generating content for Wet Toast Talk Radio

### Prerequisite

- [pdm](https://pdm.fming.dev/latest/)
- python >= 3.10
- [ffmpeg] `brew install ffmpeg`

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

## Deployment

[./aws/README.md](./aws/README.md)

## Contributing

- Commits should follow the following convention:  `refactor|feat|fix|docs|breaking|misc|chore|test: description`


## Code Standards

We use [black](https://github.com/psf/black) as our code formattter.

We use [ruff](https://beta.ruff.rs/docs/) as our linter.

We use [pytest](https://docs.pytest.org/en/6.2.x/) as our testing framework.

