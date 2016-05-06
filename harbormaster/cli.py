# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import os
import sys
import argparse

from . import engine

from logging import config
logging.config.dictConfig(
    {
        'version': 1,
        'disable_existing_loggers': True,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'harbormaster': {
                'handlers': ['console'],
                'level': 'INFO',
            },
            'compose': {
                'handlers': [],
                'level': 'INFO'
            },
            'docker': {
                'handlers': [],
                'level': 'INFO'
            }
        },
    }
)

AVAILABLE_COMMANDS = ['help', 'init', 'build', 'run']


def commandline():
    parser = argparse.ArgumentParser(description=u'Build, orchestrate, run, and '
                                                 u'ship Docker containers with '
                                                 u'Ansible playbooks')
    parser.add_argument('subcommand', choices=AVAILABLE_COMMANDS,
                        help=u'Subcommand to run - options are: {}'.format(
                            AVAILABLE_COMMANDS))
    args = parser.parse_args()
    if args.subcommand == 'help':
        parser.print_help()
        sys.exit(0)
    getattr(engine, u'cmdrun_{}'.format(args.subcommand))(os.getcwd())

