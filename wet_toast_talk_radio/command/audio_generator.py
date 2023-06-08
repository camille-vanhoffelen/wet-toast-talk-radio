import click
import structlog

from wet_toast_talk_radio.audio_generator import AudioGenerator
from wet_toast_talk_radio.audio_generator.config import validate_config
from wet_toast_talk_radio.command.print_banner import print_banner
from wet_toast_talk_radio.command.root import root_cmd

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

    logger.info("Starting audio_generator", cfg=root_cfg.audio_generator)
    audio_gen = AudioGenerator(cfg)

    audio_gen.run()


@audio_generator.command()
@click.pass_context
def benchmark(ctx: dict):
    """Benchmarks audio generation on standard script.

    Calculates:
    - run_time_in_s, the time it takes to generate the audio file
    - duration_in_s, the duration of the audio file
    - speed_ratio, the ratio between the duration and the run time
    (real time = 1, slower than real time > 1, faster than real time < 1)
    """
    root_cfg = ctx.obj["root_cfg"]
    cfg = root_cfg.audio_generator

    logger.info("Starting audio_generator", cfg=root_cfg.audio_generator)
    audio_gen = AudioGenerator(cfg)

    audio_gen.benchmark()
