# Makefile

# SHELL specifies the shell to use
SHELL := /bin/bash

# Define the dev target that does everything
setup: install_pyenv install_poetry setup_env

# Target for installing pyenv
install_pyenv:
	@if [ ! -d "$$HOME/.pyenv" ]; then \
		git clone https://github.com/pyenv/pyenv.git ~/.pyenv; \
		echo 'export PYENV_ROOT="$${HOME}/.pyenv"' >> ~/.bashrc; \
		echo 'export PATH="$${PYENV_ROOT}/bin:$${PATH}"' >> ~/.bashrc; \
		echo 'eval "$$(pyenv init --path)"' >> ~/.bashrc; \
		echo 'eval "$$(pyenv virtualenv-init -)"' >> ~/.bashrc; \
		source ~/.bashrc; \
	fi
	@pyenv install -s 3.11.0
	@pyenv global 3.11.0

# Target for installing Poetry
install_poetry:
	@if ! command -v poetry > /dev/null; then \
		curl -sSL https://install.python-poetry.org | python3 -; \
	fi

# Target to setup virtual environment and install dependencies
setup_env:
	@if [ -z "$$(pyenv versions | grep learn_ai)" ]; then \
		pyenv virtualenv 3.11.0 learn_ai; \
	fi
	@pyenv local learn_ai
	@pip install poetry==1.6.1
	@poetry install --no-cache

# Utility targets
.PHONY: setup install_pyenv install_poetry setup_env
