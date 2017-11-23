import logging
import collections
import sys
import datetime
import structlog
import contextlib
import gevent


def cwlogs_processor(_, method_name, event_dict):
    new = collections.OrderedDict()
    new['time'] = datetime.datetime.now().isoformat() + 'Z'
    new['level'] = method_name
    new['message'] = event_dict.pop('event')
    new['data'] = event_dict
    return new


class Discard(object):
    def write(self, b):
        pass


class FilteringLogger(object):
    def __init__(self, level):
        self.level = level

    def isEnabledFor(self, level):
        return self.level <= level


def bound_filter_by_level(level):
    logger = FilteringLogger(level)

    def processor(_, method_name, event_dict):
        return structlog.stdlib.filter_by_level(logger, method_name, event_dict)

    return processor


def greenlet_handler(**kwargs):
    def handler(greenlet):
        error("Greenlet crashed", exc_info=greenlet.exc_info, **kwargs)

    return handler


def add_global_values(global_values):
    def processor(_, __, event_dict):
        for key, value in global_values.items():
            if key not in event_dict:
                event_dict[key] = value
        return event_dict

    return processor


def std_processor(_, method_name, event_dict):
    event_dict['_record'] = event_dict['data'].pop('_record')
    event_dict['data']['logger'] = event_dict['_record'].name
    return event_dict


def configure(levelname, **global_values):
    try:
        level = structlog.stdlib.INFO
        if levelname:
            level = structlog.stdlib._NAME_TO_LEVEL[levelname]
    except KeyError:
        raise ValueError("Unknown log level: '%s'" % levelname)

    pre_chain = [
        # format_exc_info adds "exception" key with a traceback if it's available
        structlog.processors.format_exc_info,
        add_global_values(global_values),
        cwlogs_processor,
    ]
    processors = list(pre_chain)
    processors.extend([
        structlog.processors.JSONRenderer(),
        bound_filter_by_level(level),
    ])
    pre_chain.append(std_processor)

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=structlog.threadlocal.wrap_dict(dict),
    )

    # capturing all messages from standard python logging
    std_handler = logging.StreamHandler(stream=sys.stdout)
    std_handler.setFormatter(structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=pre_chain,
    ))
    std_logger = logging.getLogger()
    std_logger.addHandler(std_handler)
    std_logger.setLevel(level)

    # don't output raw exceptions of failed greenlets
    gevent.get_hub().exception_stream = Discard()


def bind_global(**kwargs):
    structlog.get_logger().bind(**kwargs)


@contextlib.contextmanager
def bind(**kwargs):
    with structlog.threadlocal.tmp_bind(structlog.get_logger(), **kwargs):
        yield


def debug(message, **kwargs):
    structlog.get_logger().debug(message, **kwargs)


def info(message, **kwargs):
    structlog.get_logger().info(message, **kwargs)


def warning(message, **kwargs):
    structlog.get_logger().warning(message, **kwargs)


def error(message, **kwargs):
    structlog.get_logger().error(message, **kwargs)


def critical(message, **kwargs):
    structlog.get_logger().critical(message, **kwargs)


def exception(message, **kwargs):
    structlog.get_logger().exception(message, **kwargs)
