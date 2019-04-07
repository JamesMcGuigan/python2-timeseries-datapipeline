import time
from multiprocessing import Manager

from glob2 import glob

from src.readers.CSVReader import CSVReader
from src.util.Globals import Globals
from src.util.IterableQueue import IterableQueue


def main():
    print "START - main()"

    manager   = Manager()
    queue     = manager.Queue()  # ThreadPool() works with Queue.Queue(); ProcessPool requires Autoproxy: manager.Queue()
    filenames = glob('./data/occupancy_data/*.txt')
    processes = []

    def start_reader(filename):
        print "START - start_reader(", queue, ")"
        CSVReader(filename, queue=queue, wrapper=dict, start=True)
        print "END   - start_reader(", queue, ")"
    # map(start_reader, filenames)
    processes += [ Globals().process_pool.amap(start_reader, filenames) ]


    def print_queue(queue):
        print "START - print_queue(", queue, queue.qsize(), ")"
        while queue.empty():
            time.sleep(1)
        for count, item in enumerate(IterableQueue(queue)):
            print queue.qsize(), item
        print "END - print_queue(", queue, queue.qsize(), ")"
    # print_queue(queue)
    processes += [ Globals().process_pool.apipe(print_queue, queue) ]


    ### TODO: Investigate - pathos doesn't cleanly exit process, or run final line of code
    ### TODO: Investigate - Ctrl-C - onKeyboardInterupt = RuntimeError("cannot join current thread")
    # Globals().process_pool.join()
    # for process in processes: process.join()

    print "END - main()"


if __name__ == '__main__':
    main()
