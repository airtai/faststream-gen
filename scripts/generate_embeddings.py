#!/usr/bin/env bash

set -e
set -x

python -c "from faststream_gen._components import embeddings; embeddings.app()"