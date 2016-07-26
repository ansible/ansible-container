#!/bin/bash

test '(! -f /src/requirements.txt)' || pip install --no-cache-dir -q -U -r /src/requirements.txt
"$@"
