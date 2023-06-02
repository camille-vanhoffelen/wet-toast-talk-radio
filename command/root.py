import logging
import os
from typing import Optional

import click
import structlog
import yaml

from command.config import Config

logger = structlog.get_logger()


@click.group()
@click.option("-v", "--verbose", is_flag=True)
@click.option(
    "-c", "--config", type=str, default="config.yml", help="Path to config file."
)
@click.pass_context
def root_cmd(ctx: dict, verbose: bool, config: Optional[str]):
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

    logger.debug("root_cmd hello")

    root_cfg = Config()
    if os.path.isfile(config):
        with open(config, "r", encoding="utf8") as file:
            cfg_obj = yaml.safe_load(file)
            root_cfg = Config.parse_obj(cfg_obj)

    ctx.obj["root_cfg"] = root_cfg
