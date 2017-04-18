# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

import threading

from six import with_metaclass
from six.moves import queue
from ._text import to_text

class Singleton(type):
    def __new__(cls, name, parents, params):
        try:
            return cls.__singleton__
        except AttributeError:
            cls.__singleton__ = super(Singleton, cls).__new__(cls, name, parents, params)
            return cls.__singleton__


class LogMultiplexer(with_metaclass(Singleton, object)):

    def __init__(self):
        self.q = queue.Queue()
        self.start()

    def consumer(self):
        while True:
            log_obj, message = self.q.get(block=True)
            log_obj.info(message)

    def start(self):
        consumer_thread = threading.Thread(target=self.consumer)
        consumer_thread.daemon = True
        consumer_thread.start()

    def produce(self, iterator, log_obj):
        for message in iterator:
            self.q.put((log_obj, to_text(message).rstrip()))

    def add_iterator(self, iterator, log_obj):
        producer_thread = threading.Thread(target=self.produce,
                                           args=(iterator, log_obj))
        producer_thread.daemon = True
        producer_thread.start()
