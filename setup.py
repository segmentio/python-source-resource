from setuptools import setup
import os

setup(
    name='segment_source_resource',
    packages=['segment_source_resource'],
    version='0.9.1',
    description='Abstraction to make sources easier to write',
    author='Segment',
    author_email='friends@segment.com',
    url='https://github.com/segmentio/python-source-resource',
    install_requires=[
        'pydash==3.4.3',
        'gevent==1.1.1',
        'python-dateutil==2.5.3',
        'segment_source==0.7.0'
    ]
)
