import atexit
from Queue import Empty
from multiprocessing import Queue


class FileReader:
    debug = True
    
    def __init__(self, filename, queue=None, wrapper=dict, start=False):
        if self.debug: print self.__class__.__name__, '__init__()', queue
        
        self.queue      = queue if queue is not None else Queue()
        self.filename   = filename
        self.filehandle = None
        self.wrapper    = wrapper

        atexit.register(self.onExit)
        if start == True:
            self.start()


    @property
    def reader( self ):
        if not self.filehandle:
            self.filehandle = open(self.filename, 'r', -1)
        return self.filehandle


    def start( self ):
        if self.debug: print self.__class__.__name__, 'start()', self.queue
        for linenumber, item in enumerate(self.reader):
            output = self.wrapper(item)
            self.queue.put(output)
        self.queue.put(Empty)


    def __del__(self):
        self.onExit()

    def onExit( self ):
        if self.debug: print self.__class__.__name__, 'onExit()',
        try:
            self.filehandle.close()
        except: pass
