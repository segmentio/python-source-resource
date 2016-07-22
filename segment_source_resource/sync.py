import sys

from gevent.pool import Group
import gevent

from segment_source_resource.exceptions import PublicError
from segment_source import client as source


_errors = []

def _create_error_handler(collection):
    def handler(thread):
        print("{} failed".format(collection))
        print(thread.exception)

        if isinstance(thread.exception, PublicError):
            message = thread.exception.__str__()
        else:
            message = 'Unexpected failure'
            _errors.append(thread.exception)

        source.report_error(message, collection)

    return handler


def _process_resource(resources, seed, resource):
    threads = Group()

    def consume(obj):
        morphed = resource.transform(obj, seed)
        threads.spawn(resource.set, morphed)
        threads.spawn(_enqueue_children, resources, obj, resource)

    objects = resource.fetch(seed, consume)
    threads.join()


def _enqueue_children(resources, seed, parent):
    threads = Group()
    for resource in [r for r in resources if r.parent == parent.name]:
        thread = threads.spawn(_process_resource, resources, seed, resource)
        thread.link_exception(_create_error_handler(resource.collection))

    threads.join()


def execute(resources, seed=None):
    threads = Group()
    for resource in [r for r in resources if not r.parent]:
        thread = threads.spawn(_process_resource, resources, seed, resource)
        thread.link_exception(_create_error_handler(resource.collection))

    threads.join()

    if len(_errors):
        sys.exit(1)
