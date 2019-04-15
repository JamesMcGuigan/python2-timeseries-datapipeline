from Queue import Empty
from multiprocessing.queues import Queue

from typing import Any, Callable, Dict, List, Set, Union

from .Condition import Condition



class EventManager(object):
    """
    Event Manager
    TODO: untested and unrun code

    ### Usage:

    queue         = Manager().Queue()
    event_manager = EventManager(queue, async_pool=ProcessPool()).run()

    # register events
    commands = []; responses = [];
    event_manager.register(lambda event: commands.append(event),  condition={ "type": "command"  }, options={ "async": True })
    event_manager.register(lambda event: responses.append(event), condition={ "type": "response" })

    # add events to queue to trigger events
    queue.put({ "type": "command",  "action": "test"    })
    queue.put({ "type": "response", "value":  "success" })

    # manually trigger events
    event_manager.trigger({ "type": "response", "value": "complete" })
    """
    
    def __init__(self, queue=None, debug=False, async_pool=None ):
        # type: (Queue, bool, Union['ThreadPool', 'ProcessPool']) -> None
        if queue: assert isinstance(queue, Queue)

        self.queue      = queue       # type: Queue
        self.async_pool = async_pool  # type: Union['ThreadPool', 'ProcessPool']
        self.options = {
            "async": bool(async_pool),
            "debug": bool(debug)
            }

        # NOTE: first-pass implementation is to use a unindexed list of events
        self.rules = []                     # type: List[Dict]
        self.rules_index = { None: set() }  # type: Dict[Any:Set]



    ##### Public Interface #####

    def run( self ):  # type: () -> EventManager
        if self.queue:
            while True:
                event = self.queue.get()
                if event == Empty: break
                self.trigger( event )
        return self


    def register( self, callback, condition, options=None ):
        # type: (Callable, Union[Condition,Dict], Union[Dict,None]) -> int
        assert callable(callback)

        index = len(self.rules)  # current length is same as last index after append
        rule = {
            "condition": Condition(condition),
            "callback":  callback,
            "options":   options or {},
            "index":     index
            }
        self.rules.append(rule)
        self._register_index( index, condition )

        if self.options['debug']: print self.__class__.__name__, 'register()', rule
        return index  # return value can be used by self.unregister_index()


    def register_once( self, callback, condition, options=None ):
        # type: (Callable, Union[Condition,Dict], Union[Dict,None]) -> int
        assert callable(callback)

        index = None  # this will retrospectively be updated by self.register() inside the closure
        def once_callback( event ):
            result = callback(event)
            self.unregister_index( index )
            return result

        index = self.register( once_callback, condition, options )
        return index


    def unregister( self, callback, condition=None ):  # type: (Union[int, Callable], Union[Condition,Dict]) -> None
        if isinstance(callback, int):
            self.unregister_index(callback)
        else:
            assert callable(callback)
            if self.options['debug']: print self.__class__.__name__, 'unregister(', callback.__name__, condition, ')'

            condition = Condition(condition)
            for index, rule in enumerate(self.rules):
                if (
                        rule is not None
                    and rule['callback'] == callback
                    and (condition is None) or rule['condition'] == condition
                ):
                    self.unregister_index(index)


    def unregister_index( self, index ):  # type: (int) -> None
        assert isinstance(index, int)
        if 0 < index < len(self.rules):
            rule = self.rules[index]
            self.rules[index] = None  # Use None rather than del to preserve index numbers

            self._unregister_index( index, rule['condition'] )
            if self.options['debug']: print self.__class__.__name__, 'unregister_index(', index, ')', rule


    def trigger( self, event, options=None ):  # type: (Dict, Union[Dict,None]) -> List[Any]
        if self.options['debug']: print self.__class__.__name__, 'START: trigger(', event, options, ')'

        rules   = self._match_rules( event )
        results = []
        for rule in rules:
            options = reduce(lambda a, b: a.update(b or {}) or a, [self.options, rule["options"], options], {})
            if self.options["async"]:
                result = self.async_pool.apipe( rule['callback'], event )
            else:
                try:
                    result = rule['callback'].__call__( event )
                except Exception as exception:
                    result = exception
            results.append( result )

        if self.options['debug']: print self.__class__.__name__, 'END:   trigger(', event, options, ')', results
        return results



    ##### Indexing Methods #####

    def _match_rules( self, event ):  # type: (Dict) -> List[Dict]
        rules   = []
        indices = self._match_rules_index( event )
        for index in indices:
            rule = self.rules[index]
            if rule['condition'].matches( event ):
                rules.append( rule )
        return rules


    def _match_rules_index( self,  event ):  # type: (Dict) -> List[int]
        # match all rules containing at least one event key, excluding removed rules
        indices = set( self.rules_index.get(None, []) )
        for key in event:
            if key in self.rules_index:
                indices = indices.union( self.rules_index[key] )
        for index in indices:
            if self.rules[index] is None:
                indices.remove(index)
        return sorted(indices)


    def _register_index( self, index, condition ):  # type: (int, Union[Condition,Dict]) -> None
        condition = Condition(condition)
        for key in condition.keys() + [ None ]:
            if key not in self.rules_index: self.rules_index[key] = set()
            self.rules_index[key].add(index)


    def _unregister_index( self, index, condition ):  # type: (int, Union[Condition,Dict]) -> None
        condition = Condition(condition)
        for key in condition.keys() + [ None ]:
            if key in self.rules_index:
                self.rules_index[key].remove(index)
