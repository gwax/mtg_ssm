#!/bin/bash
set -ev
if [ "${TEST_SUITE}" = "test" ]; then
    py.test --cov=mtg_ssm --strict -r w tests;
elif [ "${TEST_SUITE}" = "lint" ]; then
    pylint --rcfile=pylintrc mtg_ssm tests;
    flake8 --ignore=E501,F401,F841 -- *.py mtg_ssm tests;
else
    error_without_calling_exit;
fi
