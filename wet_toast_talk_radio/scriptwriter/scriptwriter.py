import uuid

import structlog
from langchain.base_language import BaseLanguageModel

from wet_toast_talk_radio.common.task_log_ctx import task_log_ctx
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.scriptwriter.config import ScriptwriterConfig
from wet_toast_talk_radio.scriptwriter.the_great_debate import TheGreatDebateChain
from wet_toast_talk_radio.scriptwriter import new_llm
from wet_toast_talk_radio.scriptwriter.config import validate_config

logger = structlog.get_logger()


@task_log_ctx("script_writer")
class Scriptwriter:
    """Generate radio scripts for WTTR shows"""

    def __init__(
        self, cfg: ScriptwriterConfig, media_store: MediaStore
    ):
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

        show_name = uuid.uuid4().hex + ".txt"
        self._media_store.upload_script_show(show_name=show_name, content=script)
