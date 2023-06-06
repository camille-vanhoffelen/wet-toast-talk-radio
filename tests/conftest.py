import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--intergration",
        action="store_true",
        default=False,
        help="run integration tests",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "intergration: mark test as intergration test")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--intergration"):
        # --intergration given in cli: do not skip intergration tests
        return
    skip_integration = pytest.mark.skip(reason="need --intergration low option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
