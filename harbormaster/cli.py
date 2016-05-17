# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import os
import sys
import argparse

from . import engine
from . import exceptions

from logging import config
LOGGING = {
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
                'propagate': False
            },
            'compose': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False
            },
            'docker': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False
            }
        },
        'root': {
            'handlers': ['console'],
            'level': 'ERROR'
        }
    }


AVAILABLE_COMMANDS = {'help': 'Display this help message',
                      'init': 'Initialize a new harbormaster project',
                      'build': 'Build new images based on harbormaster.yml',
                      'run': 'Run and orchestrate built images based on harbormaster.yml',
                      'push': 'Push your built images to a Docker Hub compatible registry'}

def subcmd_init_parser(subparser):
    return

def subcmd_build_parser(subparser):
    subparser.add_argument('--recreate', action='store_true',
                           help=u'Recreate the build container image',
                           dest='recreate', default=False)

def subcmd_run_parser(subparser):
    return

def subcmd_help_parser(subparser):
    return

def subcmd_push_parser(subparser):
    subparser.add_argument('--username', action='store',
                           help=(u'Username to log into registry. If not provided, '
                                 u'it is expected that your ~/.docker/config.json '
                                 u'contains your login information.'),
                           dest='username', default=None)
    subparser.add_argument('--password', action='store',
                           help=(u'Password to log into registry. If not provided, '
                                 u'you will be prompted for it.'),
                           dest='password', default=None)
    subparser.add_argument('--url', action='store',
                           help=(u'Base URL for your registry. If not provided, '
                                 u'Docker Hub will be used.'),
                           dest='url', default=None)

def commandline():
    parser = argparse.ArgumentParser(description=u'Build, orchestrate, run, and '
                                                 u'ship Docker containers with '
                                                 u'Ansible playbooks')
    parser.add_argument('--debug', action='store_true', dest='debug',
                        help=u'Enable debug output', default=False)
    subparsers = parser.add_subparsers(title='subcommand', dest='subcommand')
    for subcommand in AVAILABLE_COMMANDS:
        subparser = subparsers.add_parser(subcommand,
                                          help=AVAILABLE_COMMANDS[subcommand])
        globals()['subcmd_%s_parser' % subcommand](subparser)
    args = parser.parse_args()
    if args.subcommand == 'help':
        parser.print_help()
        sys.exit(0)
    if args.debug:
        LOGGING['loggers']['harbormaster']['level'] = 'DEBUG'
    config.dictConfig(LOGGING)

    try:
        getattr(engine, u'cmdrun_{}'.format(args.subcommand))(os.getcwd(),
                                                              **vars(args))
    except exceptions.HarbormasterAlreadyInitializedException, e:
        logger.error('Harbormaster is already initialized')
        sys.exit(1)
    except exceptions.HarbormasterNotInitializedException, e:
        logger.error('No harbormaster project data found - do you need to run "harbormaster init"?')
        sys.exit(1)
    except exceptions.HarbormasterNoAuthenticationProvided, e:
        logger.error(unicode(e))
        sys.exit(1)
    except Exception, e:
        if args.debug:
            logger.exception(unicode(e))
        else:
            logger.error(unicode(e))
        sys.exit(1)
