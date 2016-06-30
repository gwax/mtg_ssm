#!/bin/bash

CI="$CI"

set -e
set -o nounset

SCRIPT_PATH=$(dirname "$0")
SUITE="$1"

EXIT=0

if [ "$SUITE" = "test" ]; then
    echo "Running test suite"
    py.test --cov=mtg_ssm --strict -r w tests || EXIT=$?
    if [ "$CI" = "true" ]; then
        coveralls || EXIT=$?
    fi

elif [ "$SUITE" = "lint" ]; then
    echo "Running lint suite"
    pylint \
        --rcfile="$SCRIPT_PATH"/pylintrc \
        "$SCRIPT_PATH"/mtg_ssm \
        || EXIT=$?
    pylint \
        --rcfile="$SCRIPT_PATH"/pylintrc \
        --disable=similarities,redefined-outer-name \
        "$SCRIPT_PATH"/tests \
        || EXIT=$?
    flake8 \
        --verbose \
        --max-complexity 10 \
        --ignore=E501,F401,F841 \
        "$SCRIPT_PATH"/*.py \
        "$SCRIPT_PATH"/mtg_ssm \
        "$SCRIPT_PATH"/tests \
        || EXIT=$?
else
    echo "Unknown test suite"
    EXIT=1
fi

echo "Exit code: $EXIT"
exit $EXIT
