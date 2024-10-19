# Makefile for running Python code

# Variables
PYTHON = python3
VENV = venv
ACTIVATE = . $(VENV)/bin/activate
REQUIREMENTS = requirements.txt
MAIN = main.py

# Default target to set up and run
all: run

# Create a virtual environment if not exists
$(VENV)/bin/activate:
								if [ ! -d "$(VENV)" ]; then \
																echo "Creating virtual environment..."; \
																$(PYTHON) -m venv $(VENV); \
								else \
																echo "Virtual environment already exists."; \
								fi

# Install dependencies if virtual environment is newly created
install: $(VENV)/bin/activate
								if [ ! -d "$(VENV)" ]; then \
																$(ACTIVATE) && pip install -r $(REQUIREMENTS); \
								else \
																$(ACTIVATE); \
								fi

# Run the Python program
run: install
								$(ACTIVATE) && $(PYTHON) $(MAIN)

# Clean up generated files
clean:
								rm -rf $(VENV) __pycache__ *.pyc

.PHONY: all install run clean




