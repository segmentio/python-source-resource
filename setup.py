from setuptools import setup

setup(
    name='segment_source_resource',
    packages=['segment_source_resource'],
    version='0.30.0',
    description='Abstraction to make sources easier to write',
    author='Segment',
    author_email='friends@segment.com',
    url='https://github.com/segmentio/python-source-resource',
    install_requires=[
        'pydash',
        'gevent',
        'python-dateutil',
        'segment_source==v0.30.0',
        'structlog',
    ],
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
)
