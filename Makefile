PYTHON = python
VENV = venv
PIP = $(VENV)/bin/pip
PYTEST = $(PYTHON) -m pytest

.PHONY: all install run test clean

all: install run

install: $(VENV)/bin/activate
	$(PIP) install -r requirements.txt

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)

run:
	$(PYTHON) -m processamento.main

test:
	$(PYTEST) testes/ -v

clean:
	rm -rf dados/saida/*.json
	rm -rf .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
