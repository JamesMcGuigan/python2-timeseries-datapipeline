import time
from Queue import Empty
from multiprocessing import Queue

from sortedcontainers import SortedDict  # DOCS: http://www.grantjenks.com/docs/sortedcontainers/sorteddict.html
from typing import Union, Callable, Any

from src.util.MultiProcessing import MultiProcessing


class QueueMultiplexer(object):
    '''
    QueueMultiplexer allows several input queues to be merged into a single output queue

    BaseClass implements round-robin FIFO queue multiplexer

    ### Usage:
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
        "maxsize": 0  # type: int
    }

    def __init__(self, *args, **kwargs):
        super(QueueMultiplexer, self).__init__()
        self.options      = reduce(lambda a, b: dict(a, **b), list(args) + [kwargs])  # join all arguments into single dict
        self.input_queues = []
        self.output_queue = self._construct_output_queue()
        self.thread_pool  = MultiProcessing().GlobalThreadPool()

    def _construct_input_queue( self ):   # type: () -> Queue
        return Queue(maxsize=self.options['maxsize'])

    def _construct_output_queue( self ):  # type: () -> Queue
        return Queue(maxsize=self.options['maxsize'])

    def register_input_queue( self, queue=None ): # type: (Union[Queue, None]) -> Queue
        if queue is None:
            queue = self._construct_input_queue()
        self.input_queues.append(queue)
        return queue

    def run( self ):  # type: () -> QueueMultiplexer
        '''Starts a new thread to watch input and output queues. Returns self for chaining'''
        self.thread_pool.apipe(self._run_thread, self.input_queues, self.output_queue, self.options)
        return self

    def _run_thread( self ):  # type: () -> None
        self._run_thread_wait()
        self._run_thread_loop()

    def _run_thread_wait( self ):  # type: () -> None
        '''Wait for at least one input queue to be registered before starting _run_thread_loop()'''
        while self._should_thread_terminate():
            time.sleep(0.1)

    def _should_thread_terminate( self ):  # type: () -> bool
        return len(self.input_queues) == 0 or not any(self.input_queues)

    def _run_thread_loop( self ):
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
    '''
    Sorted queue multiplexer

    ### Usage:
    multiplexer = SortedQueueMultiplexer(sort_key='timestamp', sort_direction='min', max_size=100).run()

    input_queue_1 = multiplexer.register_input_queue()
    input_queue_2 = multiplexer.register_input_queue()

    input_queue_1.put("value_1")
    input_queue_1.put(Queue.Empty)
    input_queue_2.put("value_2")
    input_queue_1.put(Queue.Empty)

    while True:
        item = multiplexer.output_queue.get()
        if item == Queue.Empty: break

    '''

    defaults = dict(QueueMultiplexer.defaults, **{
        "maxsize":        0,     # type: int
        "sort_key":       None,  # type: Union[str,list,Callable]
        "sort_direction": "min"  # type: str
    })

    def __init__(self, *args, **kwargs):
        super(SortedQueueMultiplexer, self).__init__(*args, **kwargs)

        self.sort_pop_index = { "min": 0, "max": -1 }.get( self.options['sort_direction'], 0 )
        self.peek_buffer    = SortedDict([], key=self._sort_key)


    def _sort_key( self, item ):  # type: (Any) -> None
        '''Sort function used by SortedDict peek_buffer'''

        output = item

        if self.options['sort_key'] is None:
            pass  # short-circuit common case

        elif callable( self.options['sort_key'] ):
            output = self.options['sort_key'].__call__( item )

        elif isinstance(self.options['sort_key'], (str,list)):
            # extracts nested key "a.b.c" or ["a", "b", "c"] and evaluates result if lambda() = pydash._result()
            # was: output = pydash.result(item, self.options['sort_key'])

            sort_keys = self.options['sort_key']
            if isinstance(self.options['sort_key'], str):
                sort_keys = sort_keys.split('.')
            for key in sort_keys:
                try:
                    if key in output:          output = output[key]
                    elif hasattr(output, key): output = getattr(output, key)
                    else:                      output = None

                    if callable(output):       output = output.__call__()
                    if output is None:         break
                except:
                    output = None
                    break

        return output


    def _update_peek_buffer( self, n ):  # type: (int) -> None
        '''
        updates numbered slot in peek_buffer from relevant input_queue
        noop if peek_buffer is already populated or input_queue has been terminated
        will terminate input_queue if Queue.Empty is returned
        blocks thread when input_queue is empty
        '''
        if (not n in self.peek_buffer) and (self.input_queues[n] is not None):
            item = self.input_queues[n].get()  # will block if input queue is empty
            if item is Empty:
                self.input_queues[n] = None    # terminate input_queue
                del self.peek_buffer[n]        # remove from SortedDict
            else:
                self.peek_buffer[n]  = item


    def _run_thread_loop( self ):  # type: () -> None
        '''
        Sorts input_queue data using using SortedDict peek_buffer, and outputs ordered data into output_queue
        '''
        while not self._should_thread_terminate():  # exit loop when all input_queues = None
            # Create peek_buffer entries for any new input_queues since last loop
            for n in range( len(self.peek_buffer), len(self.input_queues) ):
                self._update_peek_buffer(n)

            # Grab next min/max item from the SortedDict peek_buffer, and add it to the output_queue
            (index, item) = self.peek_buffer.popitem( self.sort_pop_index )
            self.output_queue.put(item)             # will block if output queue is full

            # Read the next value from the same input_queue
            self._update_peek_buffer(index)
