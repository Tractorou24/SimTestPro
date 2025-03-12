"""Main entry point for the application."""

import logging
import sys


def main(args: list[str]) -> int:
    """Parse arguments and run the application."""
    logging.info("Hello, world!")
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="<SimTestPro> %(asctime)s - %(levelname)s: %(message)s",
    )
    sys.exit(main(sys.argv[1:]))
