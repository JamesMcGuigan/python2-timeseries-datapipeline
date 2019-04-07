import csv

from .FileReader import FileReader


class CSVReader(FileReader):

    @property
    def reader( self ):
        if not self.filehandle:
            self.filehandle = open(self.filename, 'r', -1)
            self._reader    = csv.DictReader(self.filehandle)
        return self._reader
