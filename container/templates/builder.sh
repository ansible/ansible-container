#!/bin/bash

test '(! -f /src/requirements.txt)' || pip install --no-cache-dir -q -U -r /src/requirements.txt

roles=$(python -c "import yaml; roles = yaml.load(open('./requirements.yml', 'r')); print 0 if not roles else len(roles)")
if [ ${roles} > 0 ]; then
    ansible-galaxy install -r ./requirements.yml
fi

"$@"
