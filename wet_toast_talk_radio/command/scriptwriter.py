import click
import structlog

from wet_toast_talk_radio.command.print_banner import print_banner
from wet_toast_talk_radio.command.root import root_cmd
from wet_toast_talk_radio.media_store import new_media_store
from wet_toast_talk_radio.scriptwriter import Scriptwriter
from wet_toast_talk_radio.scriptwriter.config import validate_config

logger = structlog.get_logger()


@root_cmd.group()
@click.pass_context
def scriptwriter(ctx: dict):
    """scriptwriter generates scripts for WTTR shows"""
    print_banner("scriptwriter_banner.txt")
    root_cfg = ctx.obj["root_cfg"]
    validate_config(root_cfg.scriptwriter)


@scriptwriter.command(help="Run scriptwriter")
@click.pass_context
def run(ctx: dict):
    """Run command
    scriptwriter run TOPIC

    with TOPIC the topic of The Great Debate show.
    """
    root_cfg = ctx.obj["root_cfg"]
    sw_cfg = root_cfg.scriptwriter
    ms_cfg = root_cfg.media_store

    media_store = new_media_store(ms_cfg)
    writer = Scriptwriter(cfg=sw_cfg, media_store=media_store)
    writer.run()

# TODO allow CLI run w/ topic
@scriptwriter.command(help="Run scriptwriter")
@click.pass_context
@click.argument("topic")
def the_great_debate(ctx: dict, topic: str):
    """Run command
    scriptwriter run TOPIC

    with TOPIC the topic of The Great Debate show.
    """
    root_cfg = ctx.obj["root_cfg"]
    sw_cfg = root_cfg.scriptwriter

    # logger.info("Starting scriptwriter", cfg=root_cfg.scriptwriter)
    # writer = Scriptwriter(cfg=sw_cfg)

    # writer.run(topic=topic)
    pass
