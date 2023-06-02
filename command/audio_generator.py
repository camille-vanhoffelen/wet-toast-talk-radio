import click
import structlog

from command import root_cmd
from command.print_banner import print_banner
from audio_generator.config import validate_config
from audio_generator import AudioGenerator

logger = structlog.get_logger()


@root_cmd.group()
@click.pass_context
def audio_generator(ctx: dict):
    """audio_generator generates audio files from text files"""
    print_banner("audio_generator_banner.txt")
    root_cfg = ctx.obj["root_cfg"]
    validate_config(root_cfg.audio_generator)


@audio_generator.command(help="Run audio_generator")
@click.pass_context
def run(ctx: dict):
    """Run command"""
    root_cfg = ctx.obj["root_cfg"]
    cfg = root_cfg.audio_generator

    audio_gen = AudioGenerator(cfg)

    logger.info("Starting audio_generator", cfg=root_cfg.audio_generator)
    audio_gen.run()
