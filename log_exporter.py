
import logging
from json import dumps
from time import sleep
from pytz import timezone
from requests import post
import secret
from datetime import datetime
from utils import multi_thread_map, single_thread_map, stringify_dict
from constants import SINGLE_PUSH_ATTEMPTS, SINGLE_PUSH_DELAY_SECONDS


def post_log_line_to_loki(
    loki_url: str = "http://localhost:3100/api/prom/push",
    log_datetime: str = datetime.now(timezone("UTC")).isoformat("T"),
    log_message: str = "",
    log_source: str = "",
    log_host: str = "",
    log_job: str = "",
    headers: dict = None,
    labels: dict = None,
    attempts: int = 5,
    pause: int = 5,
):
    if not isinstance(headers, dict):
        headers = {
            "Content-type": "application/json"
        }
    _labels = dict(
        source=log_source,
        job=log_job,
        host=log_host
    )
    if isinstance(labels, dict):
        _labels.update(labels)
    payload = {
        "streams": [{
            "labels": stringify_dict(_labels),
            "entries": [{
                "ts": log_datetime,
                "line": log_message
             }]
        }]
    }
    logging.debug(f"Send log line from '{log_datetime}' with labels: '{dumps(_labels)}'")
    for attempt in range(1, attempts + 1):
        try:
            response = post(loki_url, data=dumps(payload), headers=headers)
            response.close()
            if response.status_code // 100 == 2:
                return
            content = response.content
            if len(content) > 0:
                content = content.decode("utf-8")
                logging.debug(f"Got non-empty response: '{content}'")
        except Exception:
            logging.debug(f"Posting failed for attempt {attempt}")
        sleep(pause)
    logging.warning(f"Exceeded posting attempts from '{log_datetime}'")


def post_log_dict_to_loki(d: dict):
    if secret.log_job is None:
        raise ValueError("No current log job")
    log_datetime = d.pop("event_time")
    log_message = d.pop("event_message")
    post_log_line_to_loki(
        loki_url=secret.secret["loki_url"],
        log_datetime=log_datetime,
        log_message=log_message,
        log_source=secret.secret["log_source"],
        log_host=secret.secret["log_host"],
        log_job=secret.log_job,
        labels=d,
        attempts=SINGLE_PUSH_ATTEMPTS,
        pause=SINGLE_PUSH_DELAY_SECONDS
    )


def post_log_lines_to_loki(lines: list, threads: int = 0):
    logging.info(f'Post {len(lines)} lines to Loki')
    if threads < 2:
        _ = single_thread_map(post_log_dict_to_loki, lines)
    else:
        _ = multi_thread_map(post_log_dict_to_loki, lines, processes=threads, is_async=True)
