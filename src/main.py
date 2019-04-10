from Queue import Empty

from glob2 import glob

from src.readers.CSVReader import CSVReader
from src.util.MultiProcessing import MultiProcessing


def main():
    print "START - main()"

    manager   = MultiProcessing().Manager()
    queue     = manager.Queue()  # ThreadPool() works with Queue.Queue(); ProcessPool requires Autoproxy: manager.Queue()
    filenames = glob('./data/occupancy_data/*.txt')
    pool      = MultiProcessing().GlobalProcessPool(ncpus=len(filenames)+1)

    def start_reader(filename):
        print "START - start_reader(", queue, ")"
        CSVReader(filename, queue=queue, wrapper=dict, start=True)
        print "END   - start_reader(", queue, ")"
    pool.amap(start_reader, filenames)


    def print_queue(queue):
        print "START - print_queue(", queue, queue.qsize(), ")"

        queue_count = len(filenames)
        item_count  = 0

        while queue_count > 0:
            item = queue.get()
            if item == Empty:
                queue_count -= 1
            else:
                item_count += 1
                if item_count % 1000 == 0:
                    print queue.qsize(), item

        print "END - print_queue(", queue, queue.qsize(), ")"
    # print_queue(queue)
    pool.apipe(print_queue, queue)

    pool.close()
    pool.join()

    print "END - main()"


if __name__ == '__main__':
    main()
