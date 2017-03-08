from setuptools import setup


setup(
    name='segment_source_resource',
    packages=['segment_source_resource'],
    version='0.9.9',
    description='Abstraction to make sources easier to write',
    author='Segment',
    author_email='friends@segment.com',
    url='https://github.com/segmentio/python-source-resource',
    install_requires=[
        'pydash==3.4.3',
        'gevent==1.2.1',
        'python-dateutil==2.6.0',
        'segment_source>0.9'
    ],
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
)
