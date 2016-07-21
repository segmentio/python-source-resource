from segment_source_resource.exceptions import PublicError
from segment_source import client as source
import gevent
import sys

errors = []

def _create_error_handler(collection):
    def handler(job):
        print("{} failed".format(collection))
        print(job.exception)

        if isinstance(job.exception, PublicError):
            message = job.exception.__str__()
        else:
            message = 'Unexpected failure'
            errors.append(job.exception)

        source.report_error(collection, message)

    return handler

def _spawn_collection(collection, *args):
    job = gevent.spawn(*args)
    job.link_exception(_create_error_handler(collection))
    return job

def _consume_object(resources, resource, seed, obj):
    morphed = resource.transform(obj, seed)
    resource.set(morphed)

    _enqueue_children(resources, obj, resource)

def _process_resource(resources, seed, resource):
    def consume(obj):
        morphed = resource.transform(obj, seed)
        resource.set(morphed)

        _enqueue_children(resources, obj, resource)

    objects = resource.fetch(seed, consume)

def _enqueue_children(resources, seed, parent):
    target_resources = [r for r in resources if r.parent == parent.name]

    jobs = []
    for resource in target_resources:
        jobs.append(_spawn_collection(resource.collection, _process_resource,
                    resources, seed, resource))
    gevent.joinall(jobs)

def execute(resources, seed=None):
    jobs = []
    for resource in [r for r in resources if not r.parent]:
        jobs.append(_spawn_collection(resource.collection, _process_resource,
                    resources, seed, resource))
    gevent.joinall(jobs)

    if len(errors):
        sys.exit(1)
