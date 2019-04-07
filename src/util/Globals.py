import atexit
import signal
import sys
from multiprocessing import Manager

from cached_property import cached_property
from pathos.multiprocessing import ProcessPool
from pathos.threading import ThreadPool


class Globals:
    __singleton = None
    def __new__(cls, *args, **kwds):
        if Globals.__singleton is None:
            Globals.__singleton = object.__new__(cls, *args, **kwds)
        return Globals.__singleton


    def __init__( self ):
        signal.signal(signal.SIGINT, lambda x, y: self.onKeyboardInterrupt())
        atexit.register(self.atexit)


    @cached_property
    def thread_pool( self ):
        return ThreadPool()

    @cached_property
    def process_pool( self ):
        return ProcessPool()

    @cached_property
    def manager( self ):
        return Manager()


    # Class Destructor
    def __del__(self):
        # @cached_property stores in self.__dict__
        if "thread_pool"  in self.__dict__: self.thread_pool.close()
        if "process_pool" in self.__dict__: self.process_pool.close()
        if "thread_pool"  in self.__dict__: self.thread_pool.join()
        if "process_pool" in self.__dict__: self.process_pool.join()


    # https://stackoverflow.com/questions/4205317/capture-keyboardinterrupt-in-python-without-try-except
    # TODO: BUG: onKeyboardInterrupt() doesn't cleanly shutdown all child processes
    def onKeyboardInterrupt( self ):
        self.__del__()
        sys.exit(0)

    def atexit( self ):
        self.__del__()
