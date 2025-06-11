import logging
from typing import Optional, List
import sys
import os
import threading
import json
from dataclasses import dataclass
from urllib.parse import urljoin
from json import JSONDecodeError
import uuid
from functools import wraps
import inspect

import structlog
from orjson import dumps
from structlog import BytesLoggerFactory, PrintLoggerFactory
from structlog.contextvars import (
    merge_contextvars,
)
from structlog.dev import ConsoleRenderer
from structlog.processors import (
    JSONRenderer,
    StackInfoRenderer,
    TimeStamper,
    add_log_level,
    format_exc_info,
)
from structlog.types import WrappedLogger, EventDict


if hasattr(sys, '_getframe'):
    currentframe = lambda: sys._getframe(3)
else: #pragma: no cover
    def currentframe():
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[2].tb_frame.f_back
    

class LinenoProcessor:
    def __init__(self, stack_level: int = 3) -> None:
        self.stack_level = stack_level
    
    def __call__(self, logger: WrappedLogger, name: str, event_dict: EventDict):
        """
        自定义processor, 添加日志所在文件和行号

        pathname
        filename
        lineno
        """
        if self.stack_level == 3:
            f = currentframe().f_back.f_back.f_back
        else:
            f = currentframe().f_back.f_back
        co = f.f_code
        event_dict["pathname"] = co.co_filename
        event_dict["filename"] = os.path.basename(co.co_filename)
        event_dict["lineno"] = f.f_lineno
        return event_dict


def process_thread_processor(logger, method_name, event_dict):
    """
    添加进程和线程信息

    process
    thread
    thread_name
    """
    event_dict["process"] = os.getpid()
    mp = sys.modules.get('multiprocessing')
    try:
        event_dict["process_name"] = mp.current_process().name
    except Exception: #pragma: no cover
        event_dict["process_name"] = "n/a"
    t = threading.current_thread()
    event_dict["thread_name"] = t.name
    event_dict["thread"] = threading.get_ident()
    return event_dict


def make_processor_list(ignore_stacks, stack_level) -> list:
    _processor_list = [
        merge_contextvars,
        add_log_level,
        StackInfoRenderer(),
        TimeStamper(fmt="iso", utc=True),
        LinenoProcessor(stack_level),
        process_thread_processor
    ]
    return _processor_list

def init_config(
    debug: bool,
    level: str = "",
    stacks_level: int = 3,
    ignore_stacks: Optional[List[str]] = None,
):
    """
    Args:
        debug(bool): if True, log output as json, False log output as logfmt
        level(str): debug, info, warning, error, critical case-insensitive
        stacks_level (int): 一般项目用python + 文件 方式启动时, stacks_level设为3, 用其他库启动, 例如python -m hypercorn时. stacks_level 设为2
    """
    if not ignore_stacks:
        ignore_stacks = []
    _processor_list = make_processor_list(ignore_stacks=ignore_stacks, stack_level=stacks_level)
    if debug is True:
        _processor_list.append(ConsoleRenderer())
        logger_factory = PrintLoggerFactory()
    else:
        _processor_list.extend([format_exc_info, JSONRenderer(serializer=dumps)])
        logger_factory = BytesLoggerFactory()

    logger_level = getattr(logging, level.upper(), logging.INFO)
    wrapper_class = structlog.make_filtering_bound_logger(logger_level)
    structlog.configure_once(
        cache_logger_on_first_use=True,
        wrapper_class=wrapper_class,
        processors=_processor_list,
        logger_factory=logger_factory,
    )



