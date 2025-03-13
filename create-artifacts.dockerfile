# Stage 1: Build stage
FROM --platform=linux/amd64 python:3.13 AS builder

ENV PIPENV_VENV_IN_PROJECT=1
WORKDIR /tmp/project/app

# Copy only the Pipfile
COPY Pipfile .

# Install dependencies (update pip, install pipenv, and install from Pipfile)
RUN pip install --upgrade pip && \
    pip install pipenv && \
    pipenv --python 3.13 && \
    pipenv install

# Assume the installed packages are in the .venv folder; copy them to an export folder
RUN mkdir -p /artefacts/ && \
cp -r .venv/lib/python3.13/site-packages/* /artefacts/

# Stage 2: (Optional final stage, not needed if you’re only exporting artefacts)
FROM scratch AS export
COPY --from=builder /artefacts/ .
