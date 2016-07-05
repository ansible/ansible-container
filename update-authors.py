# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import subprocess

user_scores = {}

git_log = subprocess.check_output("git log --shortstat --no-merges --pretty='%aN <%aE>'",
                                  shell=True)
log_entries = git_log.strip().split('\n')
while log_entries:
    author = log_entries.pop(0)
    _ = log_entries.pop(0)
    commit_line = log_entries.pop(0)
    commit_parts = [s.strip() for s in commit_line.split(', ')]
    commit_data = {'files': 0, 'insertions': 0, 'deletions': 0}
    for clause in commit_parts:
        count, action = clause.split(' ', 1)
        if action.endswith('(+)'):
            commit_data['insertions'] += int(count)
        elif action.endswith('(-)'):
            commit_data['deletions'] += int(count)
        else:
            commit_data['files'] += int(count)
    user_score = user_scores.setdefault(author, 0)
    user_scores[author] = user_score + commit_data['insertions'] + commit_data['deletions']

user_scores = user_scores.items()
sorted_user_scores = sorted(user_scores, key=lambda tpl: tpl[1], reverse=True)

print 'Ansible Container has been contribued to by the following authors:'
print '(This list is automatically generated - please file an issue for corrections)'
print ''
for author, _ in sorted_user_scores:
    print author
