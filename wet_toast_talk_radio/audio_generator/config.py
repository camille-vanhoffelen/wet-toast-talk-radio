from pydantic import BaseModel, StrictInt


class AudioGeneratorConfig(BaseModel):
    """audio_generator config file"""

    use_s3_model_cache: bool = False
    # Renewed MQ visibility timeout set after each sentence generation
    # see: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html
    heartbeat_interval_in_s: StrictInt = 300
    clean_tmp_dir: bool = True
    use_voice_fixer: bool = False


def validate_config(cfg: AudioGeneratorConfig):
    """Validate config"""
    assert cfg is not None, "AudioGeneratorConfig must not be None"
    assert cfg.use_s3_model_cache is not None, "use_s3_model_cache must not be empty"
