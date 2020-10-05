
.PHONY: publish build

build:
	rm -rf dist/*
	python3 setup.py sdist bdist_wheel

publish:
	source ~/var/pypi.sh
	python3 -m twine upload --repository testpypi dist/*
