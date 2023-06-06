import click
import structlog

from wet_toast_talk_radio.command.print_banner import print_banner
from wet_toast_talk_radio.command.root import root_cmd
from wet_toast_talk_radio.scriptwriter import Scriptwriter
from wet_toast_talk_radio.scriptwriter.config import validate_config

logger = structlog.get_logger()


@root_cmd.group()
@click.pass_context
def scriptwriter(ctx: dict):
    print_banner("scriptwriter.txt")
    root_cfg = ctx.obj["root_cfg"]
    validate_config(root_cfg.scriptwriter)


@scriptwriter.command(help="Run scriptwriter")
@click.pass_context
def run(ctx: dict):
    """Run command"""
    root_cfg = ctx.obj["root_cfg"]
    cfg = root_cfg.scriptwriter

    logger.info("Starting scriptwriter", cfg=root_cfg.scriptwriter)
    writer = Scriptwriter(cfg)

    writer.run()
