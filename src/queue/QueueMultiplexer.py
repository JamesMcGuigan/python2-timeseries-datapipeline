import time
from Queue import Empty
from multiprocessing import Queue

import pydash as _  # DOCS: https://pydash.readthedocs.io/en/latest/api.html
from sortedcontainers import SortedDict  # DOCS: http://www.grantjenks.com/docs/sortedcontainers/sorteddict.html

from src.util.MultiProcessing import MultiProcessing


class QueueMultiplexer(object):
    '''
    QueueMultiplexer allows several input queues to be merged into a single output queue

    Usage:
    multiplexer = QueueMultiplexer().run()

    input_queue_1 = multiplexer.register_input_queue()
    input_queue_2 = Manager().Queue()
    multiplexer.register_input_queue(input_queue_2)

    input_queue_1.put("value_1")
    input_queue_1.put(Queue.Empty)
    input_queue_2.put("value_2")
    input_queue_1.put(Queue.Empty)

    while True:
        item = multiplexer.output_queue.get()
        if item == Queue.Empty: break
    '''

    defaults = {
        "maxsize": 0
    }

    def __init__(self, **kwds):
        super(QueueMultiplexer, self).__init__(**kwds)
        self.options      = dict(self.defaults, **kwds)
        self.input_queues = []
        self.output_queue = self._construct_output_queue()
        self.thread_pool  = MultiProcessing().GlobalThreadPool()
        self.run()

    def _construct_input_queue( self ):
        return Queue(maxsize=self.options['maxsize'])

    def _construct_output_queue( self ):
        return Queue(maxsize=self.options['maxsize'])

    def register_input_queue( self, queue=None ):
        if queue is None:
            queue = self._construct_input_queue()
        self.input_queues.append(queue)
        return queue

    def run( self ):
        self.thread_pool.apipe(self._run_thread, self.input_queues, self.output_queue, self.options)
        return self

    def _run_thread( self ):
        self._run_thread_wait()
        self._run_thread_loop()

    def _run_thread_wait( self ):
        # Wait for at least one input queue to be registered
        while self._should_thread_terminate():
            time.sleep(0.1)

    def _should_thread_terminate( self ):
        return len(self.input_queues) == 0 or not any(self.input_queues)

    def _run_thread_loop( self ):
        '''round-robin FIFO queue multiplexer'''

        while not self._should_thread_terminate():      # exit loop when all input_queues = None
            for n, input_queue in enumerate(self.input_queues):
                if input_queue is None: continue        # ignore terminated queues

                try:   item = input_queue.get_nowait()  # skip rather than block on empty but unterminated queues
                except Empty: continue                  # Queue.Empty as exception

                if item == Empty:
                    self.input_queues[n] = None         # Terminate queue
                else:
                    self.output_queue.put(item)         # Pick one up and pass it on



class SortedQueueMultiplexer(QueueMultiplexer):

    defaults = dict(QueueMultiplexer.defaults, **{
        "sort_key":       None,
        "sort_direction": "min"
    })

    def __init__(self, **kwds):
        super(SortedQueueMultiplexer, self).__init__(**kwds)

        self.sort_pop_index = { "min": 0, "max": -1 }.get( self.options['sort_direction'], 1 )
        self.peek_buffer    = SortedDict([], key=self._extract_sort_key)


    def _extract_sort_key( self, item ):
        if self.options['sort_key'] is None:
            output = item
        elif callable( self.options['sort_key'] ):
            output = self.options['sort_key'].__call__( item )
        else:
            output = _.result(item, self.options['sort_key'])  # extracts nested key "a.b.c" or ["a", "b", "c"] and evaluates result if lambda()
        return output


    def _update_peek_buffer( self, n ):
        # for n in range( len(self.peek_buffer), n+1 ): self.peek_buffer.append(None)  # len(self.peek_buffer) = n+1
        if self.input_queues[n] is not None:
            item = self.input_queues[n].get()  # will block if input queue is empty
            if item is Empty:
                self.input_queues[n] = None    # terminate input_queue
                del self.peek_buffer[n]        # remove from SortedDict
            else:
                self.peek_buffer[n]  = item


    def _run_thread_loop( self ):
        '''sorted queue multiplexer'''
        while not self._should_thread_terminate():      # exit loop when all input_queues = None

            # Refill peek_buffer
            for n in range( len(self.peek_buffer), len(self.input_queues) ):
                self._update_peek_buffer(n)

            (index, item) = self.peek_buffer.popitem( self.sort_pop_index )
            self.output_queue.put(item)        # will block if output queue is empty
            self._update_peek_buffer(index)
