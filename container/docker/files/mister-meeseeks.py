#!/usr/bin/env python2.7

"""
Hello.

I am a shim to modify sys.path to support the portable runtime in /_usr without
using the PYTHONPATH environment variable because that breaks Python 3.

I'm a bad idea. I don't wish to be here.

If you have a better idea, please put me out of my misery.

"EXISTENCE IS PAIN TO A MEESEEKS, JERRY." - Mr. Meeseeks

"""

import sys
import os

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

sys.path += ['/_usr/lib/python2.7',
             '/_usr/lib/python2.7/site-packages',
             '/_usr/lib/python2.7/dist-packages',
             '/_usr/local/lib/python2.7/site-packages',
             '/_usr/local/lib/python2.7/dist-packages']

logger.debug(u'sys.argv: %s', sys.argv)

if len(sys.argv) > 1:
    # We're being invoked with a file as our argument
    try:
        if sys.argv[1][0] != '/':
            exec_path = os.path.abspath(os.path.join(os.getcwd(), sys.argv[1]))
        else:
            exec_path = sys.argv[1]
        sys.argv.pop(0)
        logger.debug(u'%s',
                     execfile(exec_path))
    except Exception, e:
        logger.exception('What about your short game, Jerry?')
else:
    # We're being invoked with code from stdin
    code = compile(sys.stdin.read(), '<stdin>', 'exec')
    exec code in {}
