import click
import structlog

from wet_toast_talk_radio.command.print_banner import print_banner
from wet_toast_talk_radio.command.root import root_cmd
from wet_toast_talk_radio.disc_jockey import DiscJockey, Migrator
from wet_toast_talk_radio.media_store import new_media_store
from wet_toast_talk_radio.message_queue.new_message_queue import new_message_queue
from wet_toast_talk_radio.radio_operator.radio_operator import RadioOperator

logger = structlog.get_logger()


@root_cmd.group()
@click.pass_context
def disc_jockey(ctx: dict):
    """disc_jockey transcodes media files to .mp3 and uploads them to the media stream server"""
    print_banner("disc_jockey_banner.txt")
    root_cfg = ctx.obj["root_cfg"]
    logger.debug("Starting disc_jockey", cfg=root_cfg.disc_jockey)


@disc_jockey.command(help="Stream media to VosCast server")
@click.pass_context
def stream(ctx: dict):
    root_cfg = ctx.obj["root_cfg"]
    dj_cfg = root_cfg.disc_jockey
    ms_cfg = root_cfg.media_store
    mq_cfg = root_cfg.message_queue
    ro_cfg = root_cfg.radio_operator
    radio_operator = RadioOperator(ro_cfg)

    media_store = new_media_store(ms_cfg)
    message_queue = new_message_queue(mq_cfg)
    dj = DiscJockey(dj_cfg, radio_operator, media_store, message_queue)
    dj.stream()


@disc_jockey.command(
    help="Transcode latest new media files to .mp3 and upload them to the Media Store"
)
@click.pass_context
def transcode(ctx: dict):
    root_cfg = ctx.obj["root_cfg"]
    dj_cfg = root_cfg.disc_jockey
    ms_cfg = root_cfg.media_store
    ro_cfg = root_cfg.radio_operator

    media_store = new_media_store(ms_cfg)
    radio_operator = RadioOperator(ro_cfg)
    dj = DiscJockey(
        dj_cfg,
        radio_operator,
        media_store,
    )
    dj.transcode_latest_media()


@disc_jockey.command(
    help="Create a new playlist for the day and upload it to the message queue"
)
@click.pass_context
def create_playlist(ctx: dict):
    root_cfg = ctx.obj["root_cfg"]
    dj_cfg = root_cfg.disc_jockey
    ms_cfg = root_cfg.media_store
    mq_cfg = root_cfg.message_queue
    ro_cfg = root_cfg.radio_operator

    media_store = new_media_store(ms_cfg)
    message_queue = new_message_queue(mq_cfg)
    radio_operator = RadioOperator(ro_cfg)
    dj = DiscJockey(dj_cfg, radio_operator, media_store, message_queue)
    dj.create_playlist()


@disc_jockey.command(help="Copy transcoded shows to fallback playlist")
@click.pass_context
def copy_shows_to_fallback(ctx: dict):
    """Run command
    disc-jockey copy-shows-to-fallback

    Copies transcoded shows to fallback playlist.
    Allows wet toast to run on historical generations only.
    Only works with valid s3 config.
    """
    root_cfg = ctx.obj["root_cfg"]
    s3_cfg = root_cfg.media_store.s3
    migrator = Migrator(s3_cfg)
    migrator.run()
