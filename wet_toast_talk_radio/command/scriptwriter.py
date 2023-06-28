import asyncio

import click
import structlog

from wet_toast_talk_radio.command.print_banner import print_banner
from wet_toast_talk_radio.command.root import root_cmd
from wet_toast_talk_radio.media_store import new_media_store
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.media_store.virtual.media_store import VirtualMediaStore
from wet_toast_talk_radio.message_queue import new_message_queue
from wet_toast_talk_radio.scriptwriter import Scriptwriter, new_llm
from wet_toast_talk_radio.scriptwriter.adverts import Advert
from wet_toast_talk_radio.scriptwriter.config import validate_config
from wet_toast_talk_radio.scriptwriter.the_great_debate import (
    TheGreatDebate,
)

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
    mq_cfg = root_cfg.message_queue

    media_store = new_media_store(ms_cfg)
    message_queue = new_message_queue(mq_cfg)
    writer = Scriptwriter(
        cfg=sw_cfg, media_store=media_store, message_queue=message_queue
    )
    writer.run()


@scriptwriter.command(help="Write script for Advert")
@click.pass_context
def advert(ctx: dict):
    """Run command
    scriptwriter advert TOPIC
    """
    logger.info("Writing script for an advert")
    root_cfg = ctx.obj["root_cfg"]
    sw_cfg = root_cfg.scriptwriter

    llm = new_llm(cfg=sw_cfg.llm)
    show = Advert.create(llm=llm, media_store=VirtualMediaStore())
    show_id = ShowId(show_i=0, date="2012-12-21")
    asyncio.run(show.awrite(show_id=show_id))


@scriptwriter.command(help="Write script for The Great Debate")
@click.pass_context
def the_great_debate(ctx: dict):
    """Run command
    scriptwriter the-great-debate
    """
    logger.info("Writing script for The Great Debate")
    root_cfg = ctx.obj["root_cfg"]
    sw_cfg = root_cfg.scriptwriter

    llm = new_llm(cfg=sw_cfg.llm)
    show = TheGreatDebate.create(llm=llm, media_store=VirtualMediaStore())
    show_id = ShowId(show_i=0, date="2012-12-21")
    asyncio.run(show.awrite(show_id=show_id))
