import uuid

import structlog
from langchain.chat_models import ChatOpenAI

from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.scriptwriter.config import ScriptwriterConfig
from wet_toast_talk_radio.scriptwriter.the_great_debate import TheGreatDebateChain

logger = structlog.get_logger()


class Scriptwriter:
    """Generate radio scripts for WTTR shows"""

    llm_model: str = "gpt-3.5-turbo"
    llm_temperature: float = 0.9

    def __init__(self, cfg: ScriptwriterConfig, media_store: MediaStore):
        self._cfg = cfg
        self._media_store = media_store

    def run(self, topic: str) -> None:
        llm = ChatOpenAI(
            openai_api_key=self._cfg.openai_api_key,
            model=self.llm_model,
            temperature=self.llm_temperature,
        )
        chain = TheGreatDebateChain.from_llm(llm=llm)

        logger.info("Writing The Great Debate show...", topic=topic)
        outputs = chain(inputs={"topic": topic})
        script = outputs["script"]
        logger.info("Finished writing The Great Debate show", script=script)

        show_name = uuid.uuid4().hex + ".txt"
        self._media_store.upload_script_show(show_name=show_name, content=script)
