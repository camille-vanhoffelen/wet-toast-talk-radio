from pydantic import BaseModel


class ScriptwriterConfig(BaseModel):
    """scriptwriter config file"""

    openai_api_key: str


def validate_config(cfg: ScriptwriterConfig):
    """Validate config"""
    assert cfg is not None, "ScriptwriterConfig must not be None"
    assert cfg.openai_api_key, "OpenAI API Key must not be empty"
