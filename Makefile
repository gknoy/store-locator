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
ifeq ($(OS),Windows_NT)
	VENV_BIN=$(ENV)\\Scripts
	PIP=$(ENV)\\Scripts\\pip
	PYTHON=$(ENV)\\Scripts\\python
	FLAKE8=$(ENV)\\Scripts\\flake8
	COVERAGE=$(ENV)\\Scripts\\coverage
endif

prepare-venv:
	# @virtualenv env
	# python3.6 -m venv env --without-pip
	# curl https://bootstrap.pypa.io/get-pip.py | python3
	@$(PIP) install -r requirements.txt
	@$(PYTHON) -m pip install --upgrade pip

lint:
	@$(FLAKE8) --exclude=$(ENV) --max-line-length=120

test: lint
	@$(COVERAGE) run -m unittest discover -s tests
	@echo ''
	@$(COVERAGE) report -m find_store.py
