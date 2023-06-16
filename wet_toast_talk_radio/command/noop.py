import click
import structlog

from wet_toast_talk_radio.command.root import root_cmd

logger = structlog.get_logger()


@root_cmd.command(help="no oop command")
@click.pass_context
def noop(ctx: dict):
    root_cfg = ctx.obj["root_cfg"]
    logger.info("Hello from noop", cfg=root_cfg)
