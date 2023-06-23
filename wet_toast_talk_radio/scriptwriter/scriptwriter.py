import structlog

from wet_toast_talk_radio.common.task_log_ctx import task_log_ctx
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.common.date import get_current_iso_utc_date
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.scriptwriter import new_llm
from wet_toast_talk_radio.scriptwriter.config import ScriptwriterConfig, validate_config
from wet_toast_talk_radio.scriptwriter.the_great_debate import TheGreatDebateChain

logger = structlog.get_logger()


@task_log_ctx("script_writer")
class Scriptwriter:
    """Generate radio scripts for WTTR shows"""

    def __init__(self, cfg: ScriptwriterConfig, media_store: MediaStore):
        self._cfg = cfg
        validate_config(cfg)
        self._llm = new_llm(cfg=cfg.llm)
        self._media_store = media_store

    def run(self, topic: str) -> None:
        chain = TheGreatDebateChain.from_llm(llm=self._llm)

        logger.info("Writing The Great Debate show...", topic=topic)
        outputs = chain(inputs={"topic": topic})
        script = outputs["script"]
        logger.info("Finished writing The Great Debate show", script=script)

        # TODO the date should be the date of the show, not current date
        show_id = ShowId(show_i=0, date=get_current_iso_utc_date())
        self._media_store.put_script_show(show_id=show_id, content=script)
