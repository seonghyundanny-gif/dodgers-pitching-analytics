SYSTEM_PYTHON ?= python3
VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
PIP ?= $(PYTHON) -m pip
NPM ?= npm
NODE ?= node

.PHONY: help setup data analysis report test lint check reproduce

help:
	@echo "setup      Install Python and Node dependencies"
	@echo "data       Build and validate processed analysis datasets"
	@echo "analysis   Run the player, diagnostic, team, bridge, and DiD analyses"
	@echo "report     Rebuild figures, workbook, DOCX, and PDF report"
	@echo "test       Run the automated test suite"
	@echo "lint       Run Ruff checks"
	@echo "check      Run lint and tests"
	@echo "reproduce  Rebuild all outputs and run tests"

setup:
	$(SYSTEM_PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e '.[dev]'
	$(NPM) ci

data:
	$(PYTHON) scripts/prepare/build_datasets.py
	$(PYTHON) scripts/analyze/build_comparable_teams_panel.py
	$(PYTHON) scripts/prepare/validate_data.py

analysis:
	$(PYTHON) scripts/analyze/regression_analysis.py
	$(PYTHON) scripts/analyze/regression_diagnostics.py
	$(PYTHON) scripts/analyze/team_before_after.py
	$(PYTHON) scripts/analyze/bridge_analysis.py
	$(PYTHON) scripts/analyze/difference_in_differences.py

report:
	$(PYTHON) scripts/report/generate_figures.py
	$(PYTHON) scripts/report/export_excel.py
	$(NPM) ci
	$(NODE) scripts/report/build_report.js
	@report_tmp=$$(mktemp -d); \
	if command -v libreoffice >/dev/null 2>&1; then \
		libreoffice --headless --convert-to pdf --outdir "$$report_tmp" reports/final_report.docx >/dev/null; \
		cp "$$report_tmp/final_report.pdf" reports/final_report.pdf; \
		echo "Saved reports/final_report.pdf"; \
	else \
		echo "LibreOffice not found; kept the checked-in PDF and generated DOCX only"; \
	fi; \
	rm -rf "$$report_tmp"

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

check: lint test

reproduce: data analysis report test
