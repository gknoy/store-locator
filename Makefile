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
else:
	VENV_BIN=$(ENV)/bin
	VENV_ACTIVATE=$(ENV)/bin/activate
	PIP=$(ENV)/bin/pip
endif

prepare-venv:
	virtualenv env
	$(PIP) install -r requirements.txt

lint:
	flake8 --exclude=$(ENV) --max-line-length=120
