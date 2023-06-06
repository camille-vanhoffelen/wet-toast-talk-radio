import structlog
from langchain.chains import SequentialChain
from langchain.chat_models import ChatOpenAI

from wet_toast_talk_radio.scriptwriter.config import ScriptwriterConfig
from wet_toast_talk_radio.scriptwriter.the_great_debate import GuestGenerationChain, ScriptGenerationChain

logger = structlog.get_logger()


class Scriptwriter:
    """Generate radio scripts for WTTR shows"""

    def __init__(self, cfg: ScriptwriterConfig):
        self._cfg = cfg

    def run(self) -> None:
        topic = "toilet paper"
        chat = ChatOpenAI(openai_api_key=self._cfg.openai_api_key, model="gpt-3.5-turbo", temperature=0.9)
        chain = SequentialChain(chains=[GuestGenerationChain(llm=chat), ScriptGenerationChain(llm=chat)],
                                input_variables=["topic"],
                                output_variables=["in_favor_guest", "against_guest", "script"],
                                verbose=True)
        response = chain(inputs={"topic": topic})
        logger.info(response)
