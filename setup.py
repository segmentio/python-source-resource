from setuptools import setup
import os

setup(
    name = 'source_resource',
    version = '0.0.1',
    packages=[
        'source_resource'
    ],
    install_requires=[
        'pydash==3.4.3',
        'python-dateutil==2.5.3',
        'source==0.0.2'
    ]
)
