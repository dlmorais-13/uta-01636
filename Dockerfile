FROM python:3.10-slim AS builder

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Poetry configurations
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

# Add Poetry executable to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install curl to fetch Poetry installation script
RUN apt-get update && apt-get install --no-install-recommends -y curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copy dependency definition files first to leverage Docker layer caching
COPY pyproject.toml poetry.lock ./

# Install dependencies. --no-root prevents installing the project module itself in this layer
RUN poetry install --no-root --only main

# Prioritize the virtual environment's binaries in the system PATH
ENV PATH="/code/.venv/bin:$PATH"

# Copy application source code into the container
COPY ./src /code/src
COPY ./daycent /daycent

# Run the main module
CMD ["python", "-m", "src.main"]
