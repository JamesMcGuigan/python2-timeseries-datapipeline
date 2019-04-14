import time
from Queue import Empty
from multiprocessing import Queue
from operator import itemgetter
from sortedcontainers import SortedList
from typing import Any, Callable, Union

from src.util.MultiProcessing import MultiProcessing



class QueueMultiplexer(object):
    """
    QueueMultiplexer allows several input queues to be merged into a single output queue

    This class implements a non-blocking round-robin FIFO queue multiplexer
    See SortedQueueMultiplexer() subclass for a sorted/chronological queue multiplexer with blocking

    ### Usage:
    multiplexer = QueueMultiplexer().run()       # chaining .run() is suitable for one-to-many multiplexing

    input_queue_1 = multiplexer.input_queue()                   # generate new input_queue
    input_queue_2 = multiplexer.input_queue(Manager().Queue())  # register external input_queue
    output_queue  = multiplexer.output_queue()   # multiple output queues can be registered
    multiplexer.run()                            # many-to-many multiplexing requires registering queues before .run()

    input_queue_1.put("value_1")                 # input data from other processes into input queues
    input_queue_2.put("value_2")
    input_queue_1.put(Queue.Empty)               # mark termination of each input queue with Queue.Empty
    input_queue_2.put(Queue.Empty)

    while True:
        item = output_queue.get()                # "value_1", "value_2"
        if item == Queue.Empty: break            # a single Queue.Empty is returned when all input queues have been terminated
    """

    defaults = {
        "maxsize_input":  0,            # type: int
        "maxsize_output": 0,            # type: int
        "wait_for_n_input_queues":  1,  # type: int
        "wait_for_n_output_queues": 1,  # type: int
        }


    def __init__( self, *args, **kwargs ):
        super(QueueMultiplexer, self).__init__()

        self.options        = reduce(lambda a, b: dict(a, **b), [self.defaults] + list(args) + [kwargs])  # join arguments into single dict
        self.is_running     = False
        self._input_queues  = []
        self._output_queues = []
        self.thread_pool    = MultiProcessing().GlobalThreadPool()  # Handles thread cleanup on program termination


    def _construct_input_queue( self ):  # type: () -> Queue
        return Queue(maxsize=self.options['maxsize_input'])


    def _construct_output_queue( self ):  # type: () -> Queue
        return Queue(maxsize=self.options['maxsize_output'])


    def input_queue( self, queue=None ):  # type: (Union[Queue, None]) -> Queue
        """registers/generates a new input queue to watch"""
        if queue is not None:
            assert hasattr(queue, 'get'), 'input_queue(queue) must be of type Manager().Queue()'
            assert hasattr(queue, 'put'), 'input_queue(queue) must be of type Manager().Queue()'
        else:
            queue = self._construct_input_queue()
        self._input_queues.append(queue)
        return queue


    def output_queue( self, queue=None ):  # type: (Union[Queue, None]) -> Queue
        """registers/generates a new output queue"""
        if queue is not None:
            assert hasattr(queue, 'get'), 'output_queue(queue) must be of type Manager().Queue()'
            assert hasattr(queue, 'put'), 'output_queue(queue) must be of type Manager().Queue()'
        else:
            queue = self._construct_output_queue()
        self._output_queues.append(queue)
        return queue


    def run( self ):  # type: () -> QueueMultiplexer
        """
        Starts a new thread to watch input and output queues.

        Returns self for chaining from constructor, which is suitable for one-to-many / many-to-one queue multiplexing.

        If multiplexing many-to-many input/output queues, all queues should be registered before .run()
            to avoid race-condition dataloss or mis-ordering from unregistered queues
            otherwise set: wait_for_n_input_queues= / wait_for_n_output_queues= in constructor arguments
        """
        if not self.is_running:  # semaphore to prevent running multiple threads
            self.is_running = True
            self.thread_pool.apipe(self._run_thread)
        return self


    def _run_thread( self ):  # type: () -> None
        self._run_thread_wait()
        self._run_thread_loop()
        self._run_thread_complete()


    def _run_thread_wait( self ):  # type: () -> None
        """Wait for at least one input/output queue to be registered before starting _run_thread_loop()"""
        while ( len(self._input_queues)  < self.options['wait_for_n_input_queues']
            and len(self._output_queues) < self.options['wait_for_n_output_queues']
            and self._should_thread_terminate()
        ):
            time.sleep(0.1)


    def _should_thread_terminate( self ):  # type: () -> bool
        return len(self._input_queues)  == 0 or not any(self._input_queues) \
            or len(self._output_queues) == 0 or not any(self._output_queues)


    def _run_thread_loop( self ):
        """Implements a non-blocking round-robin FIFO queue multiplexer"""
        while not self._should_thread_terminate():      # exit loop when all input_queues = None
            for n, input_queue in enumerate(self._input_queues):
                if input_queue is None: continue        # ignore terminated queues

                try:   item = input_queue.get_nowait()  # skip rather than block on empty but unterminated queues
                except Empty: continue                  # Queue.Empty as exception

                if item == Empty:
                    self._input_queues[n] = None        # Terminate queue
                    continue

                # Add item to all output_queues
                for output_queue in self._output_queues:
                    output_queue.put(item)


    def _run_thread_complete( self ):
        # Add Queue.Empty to all output_queues, once all input has been read
        for output_queue in self._output_queues:
            output_queue.put(Empty)



class SortedQueueMultiplexer(QueueMultiplexer):
    """
    Sorted queue multiplexer

    ### Usage:

    # For one-to-many, or many-to-one multiplexing, .run() can be safely chained to the constructor
    multiplexer = SortedQueueMultiplexer(sort_key='timestamp', sort_direction='min', max_size=100).run()

    input_queue_1 = multiplexer.input_queue()                   # generate new input_queue
    input_queue_2 = multiplexer.input_queue(Manager().Queue())  # register external input_queue
    output_queue  = multiplexer.output_queue()   # multiple output queues can be registered
    multiplexer.run()                            # many-to-many multiplexing requires registering queues before .run()

    # data in input queues is assumed to be ordered
    input_queue_1.put({ "timestamp": 1010 })
    input_queue_1.put({ "timestamp": 1020 })
    input_queue_1.put({ "timestamp": 1030 })

    input_queue_2.put({ "timestamp": 1019 })
    input_queue_2.put({ "timestamp": 1020 })
    input_queue_2.put({ "timestamp": 1021 })

    # mark termination of each input queue with Queue.Empty
    input_queue_1.put(Queue.Empty)
    input_queue_2.put(Queue.Empty)

    while True:
        item = output_queue.get()                # 1010, 1019, 1020, 1020, 1021, 1030
        if item == Queue.Empty: break            # a single Queue.Empty is returned when all input queues have been terminated
    """

    defaults = dict(QueueMultiplexer.defaults, **{
        "maxsize_input":  0,             # type: int
        "maxsize_output": 0,             # type: int
        "wait_for_n_output_queues": 1,   # type: int
        "sort_key": None,                # type: Union[str,list,Callable]
        "sort_reverse": False            # type: bool
        })


    def __init__( self, *args, **kwargs ):
        super(SortedQueueMultiplexer, self).__init__(*args, **kwargs)

        self.sort_pop_index   = 0 if self.options['sort_reverse'] == False else -1
        self.peek_buffer_dict = {}
        self.peek_buffer_list = SortedList(key=itemgetter(0,1))  # sort on (sort_key, index)


    def _sort_key( self, item ):  # type: (Any) -> Any
        """Sort function used by SortedDict peek_buffer"""

        output = item

        if self.options['sort_key'] is None:
            pass  # short-circuit common case

        elif callable( self.options['sort_key'] ):
            output = self.options['sort_key'].__call__(item)

        elif isinstance(self.options['sort_key'], (str, list)):
            # extracts nested key "a.b.c" or ["a", "b", "c"] and evaluates result if callable()
            # was: output = pydash.result(item, self.options['sort_key'])

            sort_keys = self.options['sort_key']
            if isinstance(self.options['sort_key'], str):
                sort_keys = sort_keys.split('.')
            for key in sort_keys:
                try:
                    if key in output:          output = output[key]    # output["a"]["b"]["c"]
                    elif hasattr(output, key): output = getattr(output, key)
                    else:                      output = None

                    if callable(output):       output = output.__call__()
                    if output is None:         break
                except:
                    output = None
                    break

        return output


    def _update_peek_buffer( self, index, force=False ):  # type: (int) -> None
        """
        updates numbered slot in peek_buffer from relevant input_queue
        no-op if peek_buffer is already populated or input_queue has been terminated
        will terminate input_queue if Queue.Empty is returned
        blocks thread when input_queue is empty
        """
        if (force or index not in self.peek_buffer_dict) and (self._input_queues[index] is not None):
            item = self._input_queues[index].get()  # will block if input queue is empty
            if item is Empty:
                self._input_queues[index] = None    # mark input_queue as terminated
            else:
                # OPTIMIZATION: sort results in both dict() and SortedList
                # Assumes _run_thread_loop() will: self.peek_buffer_list.pop(index); del self.peek_buffer_dict[index]
                sort_key = self._sort_key(item)
                self.peek_buffer_dict[index] = (sort_key, index, item)
                self.peek_buffer_list.add(     (sort_key, index, item) )


    def _run_thread_loop( self ):  # type: () -> None
        """
        Implements a sorted/chronological queue multiplexer with blocking

        Store next entry from all input_queues in peek_buffer,
        write sorted min/max value to all output queues and update peek_buffer

        Blocks thread if any output_queue is full, or any input_queue is empty but not terminated
        """
        while not self._should_thread_terminate():  # exit loop when all input_queues = None
            # Create peek_buffer entries for any new input_queues since last loop
            for n in range(len(self.peek_buffer_dict), len(self._input_queues)):
                self._update_peek_buffer(n, force=False)

            # Grab next min/max item from the peek_buffer
            # WAS: values = sorted(self.peek_buffer_dict.values(), key=itemgetter(0,1), reverse=self.options['sort_reverse'] )
            (sort_key, index, item) = self.peek_buffer_list.pop( index=self.sort_pop_index )
            del self.peek_buffer_dict[index]

            # Add item to all output_queues, will block thread if any output queue is full
            for output_queue in self._output_queues:
                output_queue.put(item)

            # Read the next value from the same input_queue
            self._update_peek_buffer(index, force=True)
