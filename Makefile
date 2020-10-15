
.PHONY: build install uninstall docs

ls:
	@echo build install uninstall docs

build:
	rm -rf dist/*
	python3.7 setup.py sdist bdist_wheel

install:
	python3.7 -m pip install dist/gameServerBackend-0.0*.whl

uninstall:
	python3.7 -m pip uninstall gameServerBackend

#debug_uninstall:
#	rm ~/.local/lib/python3.7/site-packages/gameServerBackend*

docs:
	rm -rf docs/game_server_backend
	pdoc3 --html -o docs/ game_server_backend