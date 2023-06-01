
import os
import re
import logging
import tzlocal
import datetime
from pytz import timezone
from secret import secret
from zipfile import ZipFile, ZipInfo
from constants import LOG_ENCODING, TIME_REGEX
from utils import load_string, split_lines, remove_eol_from_string


# Example log line: 08:44.451011-0,EXCP,0,process=rphost,OSThread=1657674,Exception=d294e384-7ea6-49c6-be96-f3a6e3de1242,Descr='LoadComponent(liccspr):d294e384-7ea6-49c6-be96-f3a6e3de1242: Error loading component liccspr: '


def transform_local_time(dt: datetime.datetime) -> datetime.datetime:
    local_timezone = timezone(tzlocal.get_localzone_name())
    return local_timezone.localize(dt)


def get_file_modification_time(file: str) -> datetime.datetime:
    return transform_local_time(datetime.datetime.fromtimestamp(os.path.getmtime(file)))


def get_archive_entry_modification_time(info_entry: ZipInfo) -> datetime.datetime:
    return transform_local_time(datetime.datetime(*info_entry.date_time))


def get_event_time(s: str) -> datetime.timedelta:
    log_timezone = timezone(secret["log_timezone"])
    dt = log_timezone.localize(datetime.datetime.strptime(re.findall(TIME_REGEX, s)[0], "%M:%S.%f"))
    td = datetime.timedelta(minutes=dt.minute, seconds=dt.second, microseconds=dt.microsecond)
    return td


def get_real_event_time(s: str, offset: datetime.datetime) -> datetime.datetime:
    timedelta = get_event_time(s)
    real_time = offset + timedelta
    log_timezone = timezone(secret["log_timezone"])
    return real_time.astimezone(log_timezone)


def parse_log_lines(contains: str):
    lines = list()
    for line in split_lines(contains):
        line = remove_eol_from_string(line)
        line_head_matches = re.findall(TIME_REGEX, line)
        if len(line_head_matches) > 0:
            lines.append(line)
        else:
            lines[-1] += line
    return lines


def convert_log_line_to_tags(line: str, offset: datetime.datetime):
    columns = list()
    for chunk in line.split(","):
        chunk = chunk.strip()
        if chunk.endswith("'") and "'" in columns[-1]:
            columns[-1] += chunk.replace("'", "")
        else:
            columns.append(chunk.replace("'", ""))
    columns_dict = dict(event_message="")
    for idx in range(len(columns)):
        column = columns[idx]
        if idx == 0:
            columns_dict["event_time"] = get_real_event_time(column, offset).isoformat("T")
            columns_dict["event_duration"] = column.split("-")[-1]
        elif idx == 1:
            columns_dict["event_name"] = column
        elif idx == 2:
            columns_dict["event_level"] = column
        else:
            columns_dict["event_message"] += column
    return columns_dict


def parse_log_file(file: str):
    logging.info(f"Parse logs for file {file}")
    contents = load_string(file)
    parsed_log_lines = parse_log_lines(contents)
    last_event_time = get_event_time(parsed_log_lines[-1])
    log_start_time = get_file_modification_time(file) - last_event_time
    line_dicts = [convert_log_line_to_tags(i, log_start_time) for i in parsed_log_lines]
    return line_dicts


def parse_log_archive(archive: str):
    logging.info(f"Parse logs for archive {archive}")
    line_dicts = list()
    with ZipFile(archive, "r") as zf:
        for info_entry in zf.infolist():
            file = info_entry.filename
            if file.endswith(".log"):
                contents = zf.read(file).decode(LOG_ENCODING)
                parsed_log_lines = parse_log_lines(contents)
                last_event_time = get_event_time(parsed_log_lines[-1])
                log_start_time = get_archive_entry_modification_time(info_entry) - last_event_time
                line_dicts.extend([convert_log_line_to_tags(i, log_start_time) for i in parsed_log_lines])
    return line_dicts
