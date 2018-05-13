#
# Makefile for store-locator
#

ENV:=env

# On Windows, virtualenv makes env/Scripts instead of env/bin
# which makes all of this a lot more ugly. :(
# Normally I'd use $(ENV)/bin/whatever
VENV_BIN=$(ENV)/bin
PIP=$(ENV)/bin/pip
PYTHON=$(ENV)/bin/python
FLAKE8=$(ENV)/bin/flake8
COVERAGE=$(ENV)/bin/coverage

prepare-venv:
	@python3.6 -m venv $(ENV) --without-pip
	@curl https://bootstrap.pypa.io/get-pip.py | $(PYTHON)
	@$(PYTHON) -m pip install --upgrade pip
	@$(PIP) install -r requirements.txt

lint:
	@$(FLAKE8) --exclude=env,env-win --max-line-length=120

test: lint
	@$(COVERAGE) run -m unittest discover -s tests
	@echo ''
	@$(COVERAGE) report -m find_store.py
