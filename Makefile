PYTHON = python
VENV = venv
PYTEST = $(PYTHON) -m pytest

ifeq ($(OS),Windows_NT)
    BIN = $(VENV)/Scripts
else
    BIN = $(VENV)/bin
endif

PIP = $(BIN)/pip

.PHONY: all install run test clean

all: install run

install: $(PIP)
	$(PIP) install -r requirements.txt

$(PIP):
	$(PYTHON) -m venv $(VENV)

run:
	$(PYTHON) -m processamento.main

test:
	$(PYTEST) testes/ -v

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in [pathlib.Path('dados/saida'), pathlib.Path('.pytest_cache')]]"
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__') if p.is_dir()]"
