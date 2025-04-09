#!/bin/bash
docker compose --env-file .env.test --profile end-to-end run --build --quiet-pull end-to-end-tests ./tests/end_to_end/run.sh
test_exit_code=$?
docker compose --env-file .env.test --profile end-to-end down --volumes --remove-orphans
exit $test_exit_code
