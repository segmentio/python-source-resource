import sys

from gevent.pool import Group
import gevent

from segment_source_resource.exceptions import PublicError
from segment_source import client as source

_threads = Group()

def _create_error_handler(collection):
    def handler(thread):
        print("{} failed".format(collection))
        print(thread.exception)

        if isinstance(thread.exception, PublicError):
            message = thread.exception.__str__()
        else:
            message = 'Unexpected failure'

        source.report_error(message, collection)

    return handler


def _process_resource(resources, seed, resource):
    def consume(obj):
        morphed = resource.transform(obj, seed)
        _threads.spawn(resource.set, morphed)
        _threads.spawn(_enqueue_children, resources, obj, resource)

    objects = resource.fetch(seed, consume)


def _enqueue_children(resources, seed, parent):
    for resource in [r for r in resources if r.parent == parent.name]:
        thread = _threads.spawn(_process_resource, resources, seed, resource)
        thread.link_exception(_create_error_handler(resource.collection))


def execute(resources, seed=None):
    for resource in [r for r in resources if not r.parent]:
        thread = _threads.spawn(_process_resource, resources, seed, resource)
        thread.link_exception(_create_error_handler(resource.collection))

    _threads.join(raise_error=True)
