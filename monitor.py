#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from time import sleep
from argparse import ArgumentParser
from main import run
from utils import scan_whole_dir
from env import get_logging_level


def parse_args():
    p = ArgumentParser(description="Tool to parse and export 1C technological log into Grafana Loki")
    p.add_argument("-i", "--input_dirs", metavar="<dir>", required=True, nargs="+", help="Log directories")
    p.add_argument("-d", "--delay", metavar="<int>", default=3600, type=int, help="Seconds between scan attempts")
    ns = p.parse_args()
    return ns.input_dirs, ns.delay


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(get_logging_level())
    stream = logging.StreamHandler()
    stream.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(stream)

    input_dirs, input_delay = parse_args()
    processed_files = dict()

    while True:
        file_list = list()
        for input_dir in input_dirs:
            file_list.extend([
                i for i in scan_whole_dir(input_dir)[:-1]
                if "rphost" in i
            ])
        for file in file_list:
            if processed_files.get(file) is None:
                logging.debug(f"Processing '{file}'")
                try:
                    run(file)
                    processed_files[file] = ""
                except:
                    pass
            else:
                logging.debug(f"Skip '{file}'")
        logging.debug(f"Wait for {input_delay} seconds")
        sleep(input_delay)
