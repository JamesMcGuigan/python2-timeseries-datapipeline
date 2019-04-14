"""
Python Class to allow attribute overrides to a dictionary

Untested example code only | TODO: figure out actual base class requirements

TODO: implement keys(), has_keys(), __missing__(), __iter__() + others?
DOCS: https://rszalski.github.io/magicmethods/
"""


class AttrDict:
    def __init__(self, init=None):
        if init is not None:
            self.__dict__.update(init)

    ### Property Access
    def __getattr__(self,key):
        if key in self.__dict__:
            return self.__dict__[key]

    def __setattr__(self, key, value):
        self.__dict__[key] = value


    def to_dict( self ):
        exclude_keys = ["to_dict"]
        
        output = {}
        for key in self.__dict__.keys():
            if key not in exclude_keys:
                output[key] = self.__dict__[key]

        for key in dir(self):
            if key not in exclude_keys:
                output[key] = (key, getattr(self, key))


    ### Dictionary Access
    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __len__(self):
        return len(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)
