import asyncio
import logging

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
from wet_toast_talk_radio.scriptwriter.modern_mindfulness import (
    Circumstances,
    ModernMindfulness,
    Situations,
)
from wet_toast_talk_radio.scriptwriter.prolove import (
    Anecdotes as ProloveAnecdotes,
)
from wet_toast_talk_radio.scriptwriter.prolove import Prolove
from wet_toast_talk_radio.scriptwriter.prolove import (
    Topics as ProloveTopics,
)
from wet_toast_talk_radio.scriptwriter.the_expert_zone import (
    TheExpertZone,
)
from wet_toast_talk_radio.scriptwriter.the_expert_zone import (
    Topics as TheExpertZoneTopics,
)
from wet_toast_talk_radio.scriptwriter.the_great_debate import (
    TheGreatDebate,
    Traits,
)
from wet_toast_talk_radio.scriptwriter.the_great_debate import (
    Topics as TheGreatDebateTopics,
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


@scriptwriter.command(help="Write script for Modern Mindfulness")
@click.pass_context
def modern_mindfulness(ctx: dict):
    """Run command
    scriptwriter modern-mindfulness
    """
    logger.info("Writing script for Modern Mindfulness")
    root_cfg = ctx.obj["root_cfg"]
    sw_cfg = root_cfg.scriptwriter

    llm = new_llm(cfg=sw_cfg.llm)
    show = ModernMindfulness.create(llm=llm, media_store=VirtualMediaStore())
    show_id = ShowId(show_i=0, date="2012-12-21")
    asyncio.run(show.awrite(show_id=show_id))


@scriptwriter.command(help="Write character traits for guests")
@click.pass_context
@click.option(
    "--n-traits", default=20, type=int, help="Number of traits generated per iteration"
)
@click.option(
    "--n-iter",
    default=50,
    type=int,
    help="Number of parallel generations to be aggregated",
)
def traits(ctx: dict, n_traits: int, n_iter: int):
    """Run command
    scriptwriter traits

    Write unique character traits for guests, writes them in /tmp/traits.json
    """
    logger.info("Writing character traits")
    root_cfg = ctx.obj["root_cfg"]
    sw_cfg = root_cfg.scriptwriter
    llm = new_llm(cfg=sw_cfg.llm)
    traits_writer = Traits(llm=llm, n_traits=n_traits, n_iter=n_iter)
    asyncio.run(traits_writer.awrite())


@scriptwriter.command(help="Write topics for The Great Debate")
@click.pass_context
@click.option(
    "--n-topics", default=30, type=int, help="Number of topics generated per iteration"
)
@click.option(
    "--n-iter",
    default=10,
    type=int,
    help="Number of parallel generations to be aggregated",
)
def the_great_debate_topics(ctx: dict, n_topics: int, n_iter: int):
    """Run command
    scriptwriter the-great-debate-topics

    Write unique character topics for guests, writes them in /tmp/the-great-debate-topics.json
    """
    logger.info("Writing topics for The Great Debate")
    root_cfg = ctx.obj["root_cfg"]
    sw_cfg = root_cfg.scriptwriter
    llm = new_llm(cfg=sw_cfg.llm)

    topics_writer = TheGreatDebateTopics(llm=llm, n_topics=n_topics, n_iter=n_iter)
    asyncio.run(topics_writer.awrite())


@scriptwriter.command(help="Write situations for guided meditation")
@click.pass_context
@click.option(
    "--n-situations",
    default=30,
    type=int,
    help="Number of situations generated per iteration",
)
@click.option(
    "--n-iter",
    default=50,
    type=int,
    help="Number of parallel generations to be aggregated",
)
def situations(ctx: dict, n_situations: int, n_iter: int):
    """Run command
    scriptwriter situations

    Write unique situations for guided meditation, writes them in /tmp/situations.json
    """
    logger.info("Writing character situations")
    root_cfg = ctx.obj["root_cfg"]
    sw_cfg = root_cfg.scriptwriter
    llm = new_llm(cfg=sw_cfg.llm)
    situations_writer = Situations(llm=llm, n_situations=n_situations, n_iter=n_iter)
    asyncio.run(situations_writer.awrite())


@scriptwriter.command(help="Write bad circumstances for guided meditation")
@click.pass_context
@click.option(
    "--n-circumstances",
    default=30,
    type=int,
    help="Number of circumstances generated per iteration",
)
@click.option(
    "--n-iter",
    default=50,
    type=int,
    help="Number of parallel generations to be aggregated",
)
def circumstances(ctx: dict, n_circumstances: int, n_iter: int):
    """Run command
    scriptwriter circumstances

    Write unique bad circumstances for guided meditation, writes them in /tmp/circumstances.json
    """
    logger.info("Writing character circumstances")
    root_cfg = ctx.obj["root_cfg"]
    sw_cfg = root_cfg.scriptwriter
    llm = new_llm(cfg=sw_cfg.llm)
    circumstances_writer = Circumstances(
        llm=llm, n_circumstances=n_circumstances, n_iter=n_iter
    )
    asyncio.run(circumstances_writer.awrite())


@scriptwriter.command(help="Write script for The Expert Zone")
@click.pass_context
def the_expert_zone(ctx: dict):
    """Run command
    scriptwriter the-expert-zone
    """
    logger.info("Writing script for The Expert Zone")
    root_cfg = ctx.obj["root_cfg"]
    sw_cfg = root_cfg.scriptwriter

    llm = new_llm(cfg=sw_cfg.llm)
    show = TheExpertZone.create(llm=llm, media_store=VirtualMediaStore())
    show_id = ShowId(show_i=0, date="2012-12-21")
    asyncio.run(show.awrite(show_id=show_id))


@scriptwriter.command(help="Write topics for The Expert Zone")
@click.pass_context
@click.option(
    "--n-topics", default=30, type=int, help="Number of topics generated per iteration"
)
@click.option(
    "--n-iter",
    default=10,
    type=int,
    help="Number of parallel generations to be aggregated",
)
def the_expert_zone_topics(ctx: dict, n_topics: int, n_iter: int):
    """Run command
    scriptwriter the-expert-zone-topics

    Write unique character topics for guests, writes them in /tmp/the-expert-zone-topics.json
    """
    logger.info("Writing topics for The Expert Zone")
    root_cfg = ctx.obj["root_cfg"]
    sw_cfg = root_cfg.scriptwriter
    llm = new_llm(cfg=sw_cfg.llm)

    topics_writer = TheExpertZoneTopics(llm=llm, n_topics=n_topics, n_iter=n_iter)
    asyncio.run(topics_writer.awrite())


@scriptwriter.command(help="Write script for Prolove")
@click.pass_context
def prolove(ctx: dict):
    """Run command
    scriptwriter prolove
    """
    logger.info("Writing script for Prolove")
    root_cfg = ctx.obj["root_cfg"]
    sw_cfg = root_cfg.scriptwriter

    llm = new_llm(cfg=sw_cfg.llm)
    show = Prolove.create(llm=llm, media_store=VirtualMediaStore())
    show_id = ShowId(show_i=0, date="2012-12-21")
    asyncio.run(show.awrite(show_id=show_id))


@scriptwriter.command(help="Write topics for Prolove")
@click.pass_context
@click.option(
    "--n-topics", default=50, type=int, help="Number of topics generated per iteration"
)
@click.option(
    "--n-iter",
    default=20,
    type=int,
    help="Number of parallel generations to be aggregated",
)
def prolove_topics(ctx: dict, n_topics: int, n_iter: int):
    """Run command
    scriptwriter prolove-topics

    Write unique character topics for guests, writes them in /tmp/prolove-topics.json
    """
    logger.info("Writing topics for Prolove")
    root_cfg = ctx.obj["root_cfg"]
    sw_cfg = root_cfg.scriptwriter
    llm = new_llm(cfg=sw_cfg.llm)

    topics_writer = ProloveTopics(llm=llm, n_topics=n_topics, n_iter=n_iter)
    asyncio.run(topics_writer.awrite())


@scriptwriter.command(help="Write anecdotes for Prolove")
@click.pass_context
@click.option(
    "--n-anecdotes",
    default=50,
    type=int,
    help="Number of anecdotes generated per iteration",
)
@click.option(
    "--n-iter",
    default=20,
    type=int,
    help="Number of parallel generations to be aggregated",
)
def prolove_anecdotes(ctx: dict, n_anecdotes: int, n_iter: int):
    """Run command
    scriptwriter prolove-anecdotes

    Write unique character anecdotes for guests, writes them in /tmp/prolove-anecdotes.json
    """
    logger.info("Writing anecdotes for Prolove")
    root_cfg = ctx.obj["root_cfg"]
    sw_cfg = root_cfg.scriptwriter
    llm = new_llm(cfg=sw_cfg.llm)

    anecdotes_writer = ProloveAnecdotes(llm=llm, n_anecdotes=n_anecdotes, n_iter=n_iter)
    asyncio.run(anecdotes_writer.awrite())
