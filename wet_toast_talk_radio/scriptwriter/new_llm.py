import structlog
from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI
from langchain.llms.fake import FakeListLLM

from wet_toast_talk_radio.scriptwriter.config import LLMConfig, validate_llm_config

logger = structlog.get_logger()


def new_llm(cfg: LLMConfig) -> BaseLanguageModel:
    validate_llm_config(cfg)
    logger.debug("Creating new LLM", cfg=cfg)

    if cfg.virtual:
        return FakeListLLM(responses=cfg.fake_responses)
    else:
        return ChatOpenAI(
            openai_api_key=cfg.openai_api_key.value(),
            model=cfg.model,
            temperature=cfg.temperature,
        )
