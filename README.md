# Python2 Timeseries Data Pipeline

Proof of Concept project showing python2 data pipeline programming techniques.

Usecase inspiration was network-packet-capture validation framework for the [NASA SOFIA Project](https://www.nasa.gov/mission_pages/SOFIA/index.html)


## Instalation

```
./requirements.sh
source venv/bin/activate
py.test ./src/
```

## requirements.sh
- [src/requirements.sh](src/requirements.sh)

Generic virtualenv + pip-tools buildchain script, that creates/updates `./venv/` folders. 

Rerun after editing `./requirements.in`.

Works on my Windows / Cygwin / Unix / OSX environments and supports Python2 + Python3 


## Multiprocessing.py
- [src/util/MultiProcessing.py](src/util/MultiProcessing.py)

Singleton class wrapper around `pathos.multiprocessing` allowing for reuse of a global thread/process pool
as well as clean termination of threads/processes atexit and onKeyboardInterupt


## main.py
- [src/main.py](src/main.py)

Basic script example of reading a CSV file and passing its contents through multiprocessing.Queue() in separate threads


## FileReader / CSVReader
- [src/readers/FileReader.py](src/readers/FileReader.py)
- [src/readers/CSVReader.py](src/readers/CSVReader.py)

Simple multithreaded worker class allowing a text/csv file to be loaded line-by-line onto a Queue 


## Lex/Yacc Parser using PLY
- [src/lexer/SCLLexer.py](src/lexer/SCLLexer.py)
- [src/lexer/SCLLexer_test.py](src/lexer/SCLLexer_test.py)
- [src/lexer/SCLLexer_example.py](src/lexer/SCLLexer_example.py)
- [src/lexer/SCL.txt](src/lexer/SCL.txt)

Lex/Yacc to parse a nested SCL command syntax grammar into a nested python dictionary with unit tests

Script execution:
```
PYTHONPATH='.' src/lexer/SCLLexer_example.py
```

Input:
```
key=value(key1=value1 key2=value2 key3="string \(\"paren quoted\"\)")
```

Output:
```
[
    {
        "value": "value",
        "key": "key",
        "children": [
            {
                "value": "value1",
                "key": "key1"
            },
            {
                "value": "value2",
                "key": "key2"
            },
            {
                "value": "string (\"paren quoted\")",
                "key": "key3"
            }
        ]
    }
]
```


## QueueMultiplexer / SortedQueueMultiplexer
- [src/queue/QueueMultiplexer.py](src/queue/QueueMultiplexer.py)
- [src/queue/QueueMultiplexer_test.py](src/queue/QueueMultiplexer_test.py)

`QueueMultiplexer` is a base class that runs in a separate python thread. 
It allows clients to register multiple input and output queues of type `multiprocessing.Queue()`, 
with each item put onto an input queue is copied to every output queue. 

This can be used as a many-to-one multiplexer to join several input queues, 
or as a one-to-many multiplexer to provide multiple listeners with a full copy of the data stream.       

`SortedQueueMultiplexer` is an example of a subclass with a customizable algorithm. 
Usecase is to provide a guarantee of chronologically ordered output data (sorted by timestamp)
when dealing with multiple input files/streams that generate realtime with different frequencies and latencies.      

```
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
```

```
SortedQueueMultiplexer

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
```


## EventManager
- [src/event/EventManager.py](src/event/EventManager.py)
- [src/event/Condition.py](src/event/Condition.py)

**NOTE: untested and unrun code**

Queue based EventManger allowing for event filtering using Condition blocks.

Implements inverted indexing of condition blocks based on top-level keys (possibly over-optimised).

```
### Usage:

queue         = Manager().Queue()
event_manager = EventManager(queue, async_pool=ProcessPool()).run()

# register events
commands = []; responses = [];
event_manager.register(
    callback=lambda event: commands.append(event),
    condition={
        "name.type": [ "command", "response" ],
        "action":    lambda x: x.startsWith("test")
    },
    options={ "async": True }
)
event_manager.register(lambda event: responses.append(event), condition={ "type": "response" })

# add events to queue to trigger events
queue.put({ "name": { "type": "command", } "action": "testCommand" })
queue.put({ "type": "response", "value":  "success" })

# manually trigger events
event_manager.trigger({ "type": "response", "value": "complete" })
```
