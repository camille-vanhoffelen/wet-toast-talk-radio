from pydantic import BaseModel

from wet_toast_talk_radio.common.secret_val import SecretVar


class LLMConfig(BaseModel):
    """LLM config file"""

    virtual: bool = False
    fake_responses: list[str] = None
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.9
    openai_api_key: SecretVar[str] | None = None


def validate_llm_config(cfg: LLMConfig):
    """Validate LLM config"""
    assert cfg is not None, "LLMConfig must not be None"
    if cfg.virtual:
        assert cfg.fake_responses, "If LLM is virtual, then fake_responses must be set"
    else:
        assert (
            cfg.openai_api_key
        ), "If LLM is not virtual, then OpenAI API Key must be set"


class ScriptwriterConfig(BaseModel):
    """scriptwriter config file"""

    foo: str = "bar"
    llm: LLMConfig | None = None


def validate_config(cfg: ScriptwriterConfig):
    """Validate config"""
    assert cfg is not None, "ScriptwriterConfig must not be None"
