PYTHON := $(shell test -x .venv/bin/python && echo .venv/bin/python || echo python3)
CLAUDE ?= claude

.PHONY: install test validate demo check all clean

install:
	uv sync

test:
	$(PYTHON) -m pytest -q

validate:
	$(CLAUDE) plugin validate .
	$(CLAUDE) plugin validate plugins/greenit-studio
	$(CLAUDE) plugin validate plugins/greenit-audit
	$(CLAUDE) plugin validate plugins/greenit-engineering

demo:
	$(PYTHON) scripts/run_demo.py

check:
	$(PYTHON) scripts/check_outputs.py
	$(PYTHON) scripts/check_sources.py

all: validate test demo check

clean:
	rm -rf build .pytest_cache
	rm -rf examples/demo-service-optimized
	rm -rf dist/*
