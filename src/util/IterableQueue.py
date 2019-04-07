# Source: https://stackoverflow.com/a/21158235/748503

import Queue

class IterableQueue():

    def __init__(self,source_queue):
        self.source_queue = source_queue

    def __iter__(self):
        while True:
            try:
                yield self.source_queue.get(1)  # 1 second timeout | TODO: implement a more robust looping mechanism
            except Queue.Empty:
                return
