#
# Makefile for store-locator
#

ENV:=env

# On Windows, virtualenv makes env/Scripts instead of env/bin
# which makes all of this a lot more ugly. :(
ifeq ($(OS),Windows_NT)
	VENV_BIN=$(ENV)\\Scripts
	VENV_ACTIVATE=$(ENV)\\Scripts\\activate.bat
	PIP=$(ENV)\\Scripts\\pip
	PYTHON=$(ENV)\\Scripts\\python
	COVERAGE=$(ENV)\\Scripts\\coverage
else:
	VENV_BIN=$(ENV)/bin
	VENV_ACTIVATE=$(ENV)/bin/activate
	PIP=$(ENV)/bin/pip
	PYTHON=$(ENV)/bin/python
	COVERAGE=$(ENV)/bin/coverage
endif

prepare-venv:
	virtualenv env
	$(PIP) install -r requirements.txt

lint:
	@flake8 --exclude=$(ENV) --max-line-length=120

test: lint
	@$(COVERAGE) run -m unittest discover -s tests
	@echo ''
	@$(COVERAGE) report -m find_store.py
