import time
from multiprocessing import Queue, Manager

from glob2 import glob

from src.readers.CSVReader import CSVReader
from src.util.Globals import Globals
from src.util.IterableQueue import IterableQueue


def main():
    queue     = Queue()
    manager   = Manager()
    filenames = glob('./data/occupancy_data/*.txt')

    def start_reader(filename):
        reader = CSVReader(filename, queue=queue, wrapper=dict)
        reader.start()
    # map(start_reader, filenames)
    Globals().thread_pool.amap(start_reader, filenames)

    def print_queue(queue):
        print "print_queue(", queue, ")"
        while queue.empty(): time.sleep(0.1)
        for item in IterableQueue(queue):
            print item
    # print_queue(queue)
    Globals().thread_pool.apipe(print_queue, queue)
