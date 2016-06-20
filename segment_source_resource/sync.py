def _process_resource(resource, resources, seed):
    objects = resource.fetch(seed)

    for obj in objects:
        morphed = resource.transform(obj)
        resource.set(morphed)

        _enqueue_children(resource, resources, obj)

def _enqueue_children(parent, resources, seed):
    for resource in [r for r in resources if r.parent == parent.collection]:
        _process_resource(resource, resources, seed)

def execute(resources, seed=None):
    for resource in [r for r in resources if not r.parent]:
        _process_resource(resource, resources, seed)
