import click
import structlog

from wet_toast_talk_radio.command.print_banner import print_banner
from wet_toast_talk_radio.command.root import root_cmd
from wet_toast_talk_radio.disc_jockey import DiscJockey
from wet_toast_talk_radio.media_store import new_media_store

logger = structlog.get_logger()


@root_cmd.group()
@click.pass_context
def disc_jockey(_ctx: dict):
    """disc_jockey transcodes media files to .ogg and uploads them to the media stream server"""
    print_banner("disc_jockey_banner.txt")


@disc_jockey.command(help="Stream media to VosCast server")
@click.pass_context
def stream(ctx: dict):
    root_cfg = ctx.obj["root_cfg"]
    dj_cfg = root_cfg.disc_jockey
    ms_cfg = root_cfg.media_store

    media_store = new_media_store(ms_cfg)
    dj = DiscJockey(dj_cfg, media_store)

    logger.info("Starting disc_jockey", cfg=root_cfg.disc_jockey)
    dj.stream()


@disc_jockey.command(
    help="Transcode latest new media files to .ogg and upload them to the Media Store"
    ""
)
@click.pass_context
def transcode(ctx: dict):
    """Run command"""
    root_cfg = ctx.obj["root_cfg"]
    dj_cfg = root_cfg.disc_jockey
    ms_cfg = root_cfg.media_store

    media_store = new_media_store(ms_cfg)
    dj = DiscJockey(dj_cfg, media_store)

    logger.info("Starting disc_jockey", cfg=root_cfg.disc_jockey)
    dj.transcode_latest_media()
