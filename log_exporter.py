
from json import dumps
from time import sleep
from pytz import timezone
from requests import post
from secret import secret
from datetime import datetime
from utils import stringify_dict
from utils import multi_thread_map


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
    print("Send log line from '{}'".format(log_datetime))
    for attempt in range(1, attempts + 1):
        try:
            response = post(loki_url, data=dumps(payload), headers=headers)
            if response.status_code // 100 == 2:
                return
            content = response.content
            if len(content) > 0:
                print("Got non-empty response: '{}'".format(content.decode("utf-8")))
        except Exception:
            print(f"Posting failed for attempt {attempt}")
        sleep(pause)
    print(f"Exceeded posting attempts")


def post_log_dict_to_loki(d: dict):
    log_datetime = d.pop("event_time")
    log_message = d.pop("event_message")
    post_log_line_to_loki(
        loki_url=secret["loki_url"],
        log_datetime=log_datetime,
        log_message=log_message,
        log_source=secret["log_source"],
        log_host=secret["log_host"],
        log_job=secret["log_job"],
        labels=d,
        attempts=10
    )


def post_log_lines_to_loki(lines: list):
    print(f'Post {len(lines)} lines to Loki')
    _ = multi_thread_map(post_log_dict_to_loki, lines, is_async=True)
