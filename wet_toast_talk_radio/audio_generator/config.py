from pydantic import BaseModel


class AudioGeneratorConfig(BaseModel):
    """audio_generator config file"""

    use_s3_model_cache: bool = False


def validate_config(cfg: AudioGeneratorConfig):
    """Validate config"""
    assert cfg is not None, "AudioGeneratorConfig must not be None"
    assert cfg.use_s3_model_cache is not None, "use_s3_model_cache must not be empty"
