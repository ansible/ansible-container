#!/bin/bash

source_root=$(python -c "from os import path; print(path.abspath(path.join(path.dirname('$0'), '../..')))")
export ANSIBLE_CONTAINER_PATH=${source_root}

ansible-container --debug build --local-builder --with-variables ANSIBLE_CONTAINER_PATH="${source_root}"
