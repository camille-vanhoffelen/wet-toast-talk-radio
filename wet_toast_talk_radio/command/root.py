import logging
from pathlib import Path
from typing import Optional

import click
import structlog
import yaml

from wet_toast_talk_radio.command.config import Config

logger = structlog.get_logger()


@click.group()
@click.option("-v", "--verbose", is_flag=True)
@click.option(
    "-c", "--config", type=str, default="config.yml", help="Path to config file."
)
@click.pass_context
def root_cmd(ctx: dict, verbose: bool, config: Optional[str]):  # noqa: FBT001
    """This is an example how to run commands"""
    ctx.ensure_object(dict)

    if verbose:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        )
    else:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        )

    root_cfg = Config()
    config_path = Path(config)
    if config_path.is_file():
        with config_path.open("r", encoding="utf8") as file:
            cfg_obj = yaml.safe_load(file)
            root_cfg = Config.parse_obj(cfg_obj)

    ctx.obj["root_cfg"] = root_cfg