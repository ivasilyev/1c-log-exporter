#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from argparse import ArgumentParser
from zipfile import BadZipFile, ZipFile
import secret
from env import get_logging_level
from constants import LOGGING_TEMPLATE
from log_parser import parse_log_file, parse_log_archive
from log_exporter import post_log_lines_to_loki


def is_archive(file: str):
    if file.endswith(".zip"):
        return True
    if file.endswith(".log"):
        return False
    try:
        ZipFile(file)
        return True
    except BadZipFile:
        return False


def run(file: str):
    if is_archive(file):
        log_dicts = parse_log_archive(file)
    else:
        log_dicts = parse_log_file(file)
    post_log_lines_to_loki(log_dicts)


def parse_args():
    p = ArgumentParser(description="Tool to parse and export 1C technological log into Grafana Loki")
    p.add_argument("-i", "--input_file", metavar="<file>", required=True, help="Log file")
    ns = p.parse_args()
    return ns.input_file


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(get_logging_level())
    stream = logging.StreamHandler()
    stream.setFormatter(logging.Formatter(LOGGING_TEMPLATE))
    logger.addHandler(stream)

    input_file = parse_args()
    secret.log_job = secret.secret["log_jobs"][0]
    run(input_file)
