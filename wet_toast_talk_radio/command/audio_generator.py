from pathlib import Path

import click
import structlog

from wet_toast_talk_radio.audio_generator import AudioGenerator
from wet_toast_talk_radio.command.print_banner import print_banner
from wet_toast_talk_radio.command.root import root_cmd
from wet_toast_talk_radio.media_store import new_media_store
from wet_toast_talk_radio.message_queue import new_message_queue

logger = structlog.get_logger()


@root_cmd.group()
@click.pass_context
def audio_generator(_ctx: dict):
    """audio_generator generates audio files from text files"""
    print_banner("audio_generator_banner.txt")


@audio_generator.command(help="Run audio_generator")
@click.pass_context
def run(ctx: dict):
    """Run command"""
    root_cfg = ctx.obj["root_cfg"]
    cfg = root_cfg.audio_generator
    ms_cfg = root_cfg.media_store
    mq_cfg = root_cfg.message_queue

    media_store = new_media_store(ms_cfg)
    message_queue = new_message_queue(mq_cfg)
    audio_gen = AudioGenerator(
        cfg=cfg, media_store=media_store, message_queue=message_queue
    )

    audio_gen.run()


@audio_generator.command()
@click.pass_context
@click.option(
    "-s", "--script", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
def benchmark(ctx: dict, script: Path):
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

    text = script.read_text() if script else "Hey there! I'm a dog! Woof woof!"
    audio_gen.benchmark(script=text)
