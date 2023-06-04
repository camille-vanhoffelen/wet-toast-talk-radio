import click
import structlog

from command.print_banner import print_banner
from command.root import root_cmd
from disc_jockey import DiscJockey
from disc_jockey.config import validate_config as validate_dj_config
from media_store import new_media_store
from media_store.config import validate_config as validate_ms_config

logger = structlog.get_logger()


@root_cmd.group()
@click.pass_context
def disc_jockey(ctx: dict):
    """disc_jockey transcodes media files to mp3 and uploads them to the media stream server"""
    print_banner("disc_jockey_banner.txt")
    root_cfg = ctx.obj["root_cfg"]
    validate_dj_config(root_cfg.disc_jockey)
    validate_ms_config(root_cfg.media_store)


@disc_jockey.command(help="Stream media to VosCast server")
@click.pass_context
def stream(ctx: dict):
    root_cfg = ctx.obj["root_cfg"]
    dj_cfg = root_cfg.disc_jockey
    ms_cfg = root_cfg.media_store

    media_store = new_media_store(ms_cfg)
    dj = DiscJockey(dj_cfg, media_store)

    logger.info("Starting disc_jockey", cfg=root_cfg.disc_jockey)
    dj.streama()


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
