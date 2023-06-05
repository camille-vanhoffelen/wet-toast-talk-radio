import pathlib


def print_banner(banner_name: str):
    """Prints banner from a .txt file
    Example: print_banner("my_banner.txt")
    """
    file = pathlib.Path(__file__).with_name("resources").joinpath(banner_name)

    with file.open("r", encoding="utf8") as f:
        banner = f.read()
        print(banner)
