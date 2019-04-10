import atexit
import signal
from multiprocessing import Manager, Lock

from pathos.multiprocessing import ProcessPool
from pathos.threading import ThreadPool


class MultiProcessing:

    __singleton = None
    def __new__(self, *args, **kwds):
        if MultiProcessing.__singleton is None:
            MultiProcessing.__singleton = object.__new__(self, *args, **kwds)
        return MultiProcessing.__singleton


    def __init__( self ):
        self.manager       = None
        self.thread_pool   = None
        self.process_pool  = None
        self.lock          = None

        signal.signal(signal.SIGINT, lambda x, y: self.onKeyboardInterupt())
        atexit.register(self.onExit)


    def ThreadPool( self, *args, **kwds ):
        thread_pool = ThreadPool(*args, **kwds)
        self.register_atexit( thread_pool )
        return thread_pool


    def GlobalThreadPool( self, *args, **kwds ):
        if self.process_pool is None:
            self.process_pool = ProcessPool(*args, **kwds)
        return self.process_pool


    def ProcessPool( self, key=None, new=False, *args, **kwds ):
        process_pool = ProcessPool(*args, **kwds)
        self.register_atexit( process_pool )
        return process_pool


    def GlobalProcessPool( self, *args, **kwds ):
        if self.process_pool is None:
            self.process_pool = ProcessPool(*args, **kwds)
        return self.process_pool


    def Manager( self ):
        if self.manager is None:
            self.manager = Manager()
        return self.manager


    def Lock( self, new=False ):
        if self.lock is None:
            self.lock = Lock()
        return self.lock

        

    ### Destructors ###

    @staticmethod
    def register_atexit( pool ):
        '''staticmethod pool destructor for non-global pools'''
        print __file__, "MultiProcessing().register_atexit()", pool
        def onKeyboardInterupt():
            pool.terminate()
            pool.join()
        def onExit():
            pool.close()
            pool.join()
        signal.signal(signal.SIGINT, lambda x, y: onKeyboardInterupt())
        atexit.register(onExit)
        return pool


    def onKeyboardInterupt( self ):
        print __file__, "MultiProcessing().onKeyboardInterupt()"
        for pool in [ self.thread_pool, self.process_pool ]:
            if pool is not None:
                try:
                    pool.terminate()
                    pool.join()
                except Exception as exception: print __file__, exception


    def onExit( self ):
        print __file__, "MultiProcessing().onExit()"
        for pool in [ self.thread_pool, self.process_pool ]:
            if pool is not None:
                try:
                    pool.close()
                    pool.join()
                except Exception as exception: print exception



