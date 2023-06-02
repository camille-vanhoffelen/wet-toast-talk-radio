import click
import structlog

from command import root_cmd
from command.print_banner import print_banner
from disc_jockey.config import validate_config
from disc_jockey import DiscJockey

logger = structlog.get_logger()


@root_cmd.group()
@click.pass_context
def disc_jockey(ctx: dict):
    """disc_jockey transcodes media files to mp3 and uploads them to the media stream server"""
    print_banner("disc_jockey_banner.txt")
    root_cfg = ctx.obj["root_cfg"]
    validate_config(root_cfg.disc_jockey)


@disc_jockey.command(help="Run disc_jockey")
@click.pass_context
def run(ctx: dict):
    """Run command"""
    root_cfg = ctx.obj["root_cfg"]
    cfg = root_cfg.disc_jockey

    dj = DiscJockey(cfg)

    logger.info("Starting disc_jockey", cfg=root_cfg.disc_jockey)
    dj.run()
