
from gevent import monkey
from segment_source_resource.sync import execute


if monkey.is_module_patched('os') == False:
    monkey.patch_all()

class MockResource(object):

    def __init__(self):
        self.parent = "parent"

    def fetch(self):
        return [MockResouce()]

def test_execute():
    resource = MockResource()
    execute([resource, resource])
