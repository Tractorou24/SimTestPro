"""A report generator to prove your simulator is up to standards."""

import argparse
import logging
import signal
import sys
from pathlib import Path

from config import Config

SHOULD_QUIT = False


def _signal_handler(signum: signal.Signals, frame: any) -> None:
    """Signal handler to quit the application."""
    global SHOULD_QUIT  # noqa: PLW0603 (global-statement)
    logging.info("Received signal %d, quitting...", signum)
    SHOULD_QUIT = True


def _parse_args(raw_args: list[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-c",
        "--config",
        default="config.json",
        type=Path,
        dest="config_file",
        help="Path to the configuration file",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="report.pdf",
        type=Path,
        dest="output_file",
        help="Path to the output file",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to the output file instead of overwriting it",
    )

    return parser.parse_args(raw_args)


def main(raw_args: list[str]) -> int:
    """Run the application."""
    args = _parse_args(raw_args)
    config = Config(args.config_file)
    if config is None:
        return 1

    simconnect = SimConnect(
        config.get(["sim", "delay"]),
        config.get(["sim", "timeout"]),
    )
    return 0


if __name__ == "__main__":
    signal.signal(signal.SIGINT, _signal_handler)
    logging.basicConfig(
        level=logging.INFO,
        format="<SimTestPro> %(asctime)s - %(levelname)s: %(message)s",
    )
    sys.exit(main(sys.argv[1:]))
