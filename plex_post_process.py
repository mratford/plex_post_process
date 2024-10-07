#! /opt/homebrew/opt/python@3.12/libexec/bin/python

import argparse
import datetime
import logging
import subprocess
import re
from pathlib import Path


INTERLACED = ["^Match of the Day"]


def scan_type(file):
    command = ["/opt/homebrew/bin/mediainfo", file]
    process = subprocess.run(command, capture_output=True)
    for line in (line.decode("utf8") for line in process.stdout.splitlines()):
        if line.startswith("Scan type"):
            return line.split(":")[1].strip()

    return None


if __name__ == "__main__":
    logger = logging.getLogger("plex_post_process.py")
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(Path.home() / "log" / "plex_post_process.log")
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    parser = argparse.ArgumentParser(prog="plex_post_process")
    parser.add_argument("filename")
    args = parser.parse_args()

    source = Path(args.filename)
    dest = source.parent / (source.stem + ".mkv")

    logger.info(str(source))
    logger.info(f"Start: {datetime.datetime.now().isoformat()}")

    try:
        st = scan_type(source)
        if source.suffix == ".ts" and any(re.search(i, source.name) for i in INTERLACED):
            logger.info(f"Converting file identified as {st}")
            command = [
                "/opt/homebrew/bin/HandbrakeCLI",
                "-i",
                source,
                "-o",
                dest,
                "--comb-detect",
                "--decomb",
                "--subtitle",
                "1,2,3,4,5,6",
            ]
            process = subprocess.run(command, capture_output=True)
            if process.returncode == 0:
                source.unlink()
                logger.info("Decomb completed successfully")
                logger.info(f"Wrote to {dest}")
            else:
                logger.error(f"Decomb failed: {process.stderr}")
        else:
            logger.info(f"Nothing to do: file identified as {st}")
    except Exception as e:
        logger.error(f"Failed with exception: {e}")

    logger.info(f"Finished: {datetime.datetime.now().isoformat()}\n")
