![Wet Toast Talk Radio logo](resources/wttr-logo-thin.png)

# :bread: Wet Toast Talk Radio

Generating content for Wet Toast Talk Radio

### Prerequisite

- [pdm](https://pdm.fming.dev/latest/)
- python >= 3.10

### Config

You will likely want to create a config.yaml with these contents:

```yaml
audio_generator:
  some_setting: "foo"
disc_jockey:
  some_setting: "bar"
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

We use [pylint](https://pylint.org/) as our linter.
A [.pylintrc](.pylintrc) is given in this repo to use with pylint.

We use [pytest](https://docs.pytest.org/en/6.2.x/) as our testing framework.

