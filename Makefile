
test:
	python3 setup.py test

dist:
	python3 setup.py register -r pypi && python setup.py sdist upload -r pypi

.PHONY: dist
