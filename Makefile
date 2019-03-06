install:
    pip3 install --extra-index-url=https://packagecloud.io/segment/py-wheels/pypi/simple -r requirements.txt

test:
	python3 setup.py test

.PHONY: test install
