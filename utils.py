
import re
import multiprocessing as mp
from constants import LOG_ENCODING
from collections.abc import Callable


def load_string(file: str, encoding: str = LOG_ENCODING):
    print(f"Read '{file}'")
    with open(file=file, mode="r", encoding=encoding) as f:
        s = f.read()
        f.close()
    return s


def load_dict(file: str):
    from json import loads
    return loads(load_string(file))


def stringify_dict(d: dict):
    return "{" + ",".join([f"{k}=\"{v}\"" for k, v in d.items()]) + "}"


def split_lines(s: str):
    return re.split("[\r\n]",  s)


def load_lines(file: str):
    return [i.strip() for i in re.split("[\r\n]", load_string(file))]


def remove_empty_values(x: list):
    return [i for i in x if len(i) > 0]


def remove_eol_from_string(s: str):
    return re.sub("[\r\n\t ]+", " ", s).strip()


def split_columns(line: str):
    return line.split(",")


def load_log(file: str):
    return [remove_empty_values([j.strip() for j in split_columns(i)]) for i in remove_empty_values(load_lines(file))]


def single_thread_map(func: Callable, queue: list):
    return list(map(func, queue))


def multi_thread_map(
    func: Callable,
    queue: list,
    processes: int = 0,
    is_async: bool = False
) -> list:
    if processes == 0:
        processes = mp.cpu_count()
    pool = mp.Pool(processes=processes)
    if is_async:
        result = pool.map_async(func, queue)
    else:
        result = pool.map(func, queue)
    pool.close()
    pool.join()
    if is_async:
        return result.get()
    return result
