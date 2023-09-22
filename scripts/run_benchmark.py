#!/usr/bin/env bash

set -e
set -x

cd fixtures
python -c 'from faststream_gen._testing import benchmark; benchmark.app(".")'