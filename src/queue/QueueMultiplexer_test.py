from Queue import Empty

from . import QueueMultiplexer, SortedQueueMultiplexer



def test_QueueMultiplexer():
    multiplexer = QueueMultiplexer()             # chaining .run() is suitable for one-to-many multiplexing

    input_queue_1 = multiplexer.input_queue()    # generate new input_queue
    input_queue_2 = multiplexer.input_queue()    # register external input_queue
    output_queues = [
        multiplexer.output_queue(),              # multiple output queues can be registered
        multiplexer.output_queue(),              # multiple output queues can be registered
    ]

    # input data from other processes into input queues
    input_queue_1.put("value_1_1")
    input_queue_1.put("value_1_2")
    input_queue_2.put("value_2_1")
    input_queue_2.put("value_2_2")
    input_queue_2.put("value_2_3")

    # mark termination of each input queue with Queue.Empty
    input_queue_1.put(Empty)
    input_queue_2.put(Empty)

    # pytest doesn't like running code in separate threads, so run synchronously after all data has been loaded
    multiplexer._run_thread()

    # Read data off output queues
    output_queue_data = [ [], [] ]
    for n, output_queue in enumerate(output_queues):
        while True:
            item = output_queue.get()                # "value_1", "value_2"
            output_queue_data[n].append( item )
            if item == Empty: break                  # a single Queue.Empty is returned when all input queues have been terminated

    # Test round-robin order
    assert output_queue_data[0] == output_queue_data[1]
    assert output_queue_data[0] == [ "value_1_1", "value_2_1", "value_1_2", "value_2_2", "value_2_3",Empty ]
    assert output_queue_data[1] == [ "value_1_1", "value_2_1", "value_1_2", "value_2_2", "value_2_3",Empty ]



def test_SortedQueueMultiplexer():
    multiplexer   = SortedQueueMultiplexer(sort_key="timestamp")             # chaining .run() is suitable for one-to-many multiplexing

    input_queue_1 = multiplexer.input_queue()    # generate new input_queue
    input_queue_2 = multiplexer.input_queue()    # register external input_queue
    output_queue  = multiplexer.output_queue()   # multiple output queues can be registered

    # input data from other processes into input queues
    for n in range(1,5):
        input_queue_1.put({ "timestamp": n, "name": "input_queue_1" })

    for n in range(1,5,2):
        input_queue_2.put({ "timestamp": n, "name": "input_queue_2" })

    # mark termination of each input queue with Queue.Empty
    input_queue_1.put(Empty)
    input_queue_2.put(Empty)

    # pytest doesn't like running code in separate threads, so run synchronously after all data has been loaded
    multiplexer._run_thread()

    # Read data off output queues
    items = []
    while True:
        item = output_queue.get()                # "value_1", "value_2"
        items.append( item )
        if item == Empty: break                  # a single Queue.Empty is returned when all input queues have been terminated

    # Test round-robin order
    assert items == [
        { "timestamp": 1, "name": "input_queue_1" },
        { "timestamp": 1, "name": "input_queue_2" },
        { "timestamp": 2, "name": "input_queue_1" },
        { "timestamp": 3, "name": "input_queue_1" },
        { "timestamp": 3, "name": "input_queue_2" },
        { "timestamp": 4, "name": "input_queue_1" },
        Empty
    ]

    last_timestamp = 0
    for item in items:
        if item is not Empty:
            assert item['timestamp'] >= last_timestamp
            last_timestamp = item['timestamp']
