# Python Source Resource

Abstraction to make sources easier to write

`pip install segment_source_resource`

## Testing

```bash
pyenv virtualenv 3.5.2 python-source-resource
. /Users/ivolo/.pyenv/versions/python-source-resource/bin/activate
pip3 install -e .
make test
```

## Releasing

1. Ensure your .pypirc looks like the following:

```
[distutils]
index-servers =
   pypi

[pypi]
repository=https://pypi.python.org/pypi
username=segment
password=...
```

The password is in meldium.

2. Update "version" in setup.py
3. Tag and push tags.
4. To release to pypi:

```bash
make dist
```
