#!/bin/bash

pytest --cov=src tests/unit || {
    echo "Tests failed in tests/unit"
    exit 1
}
