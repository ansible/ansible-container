#!/bin/bash -eu

source_root=$(python -c "from os import path; print(path.abspath(path.join(path.dirname('$0'), '../../..')))")

find "${source_root}" -name '*.sh' -exec shellcheck {} +
