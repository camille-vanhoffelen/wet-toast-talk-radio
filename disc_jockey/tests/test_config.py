from disc_jockey.config import DiscJockeyConfig, validate_config


def test_config():
    cfg = DiscJockeyConfig()
    validate_config(cfg)
