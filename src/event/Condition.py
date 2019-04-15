from UserDict import IterableUserDict, UserDict
from UserList import UserList

import simplejson
from typing import Union



# Example: https://www.programcreek.com/python/example/4900/UserDict.IterableUserDict
class Condition(IterableUserDict):
    
    def __init__(self, rules=None, **kwargs):  # type: (Union[Condition,dict,None]) -> None
        IterableUserDict.__init__(self, rules, **kwargs)


    def __repr__( self ):
        return simplejson.dumps( dict(self), sort_keys=True )


    def matches( self, event, rule=None ):  # type: (dict) -> bool
        # https://stackoverflow.com/questions/9323749/python-check-if-one-dictionary-is-a-subset-of-another-larger-dictionary
        if event is None: return False
        if rule  is None: rule = self

        # Each key in rule is an AND clause
        for key in rule.keys():
            event_item = None
            if key in event:          event_item = event[key]
            elif hasattr(event, key): event_item = getattr(event, key)

            if not event_item:
                return False
            else:
                if isinstance(rule[key], (dict, UserDict)):
                    # If rule is nested dict, then search nested path for AND rules
                    if not self.matches(event_item, rule[key]):
                        return False

                elif isinstance(rule[key], (list, UserList)):
                    # a list in a rule is a OR statement (match any of the values)
                    # if event[key] is also a list, then it must contain at least one value
                    or_statement = False
                    for rule_item in rule[key]:
                        if self.compare_item( event_item, rule_item ):
                            or_statement = True
                            continue
                    if not or_statement:
                        return False
                    
                else:
                    # Scalar rules use equality matching
                    if not self.compare_item( event_item, rule[key] ):
                        return False

        return True

    @staticmethod
    def compare_item( event_item, rule_item ):
        if callable(rule_item):
            rule_item = rule_item.__call__()

        if isinstance(event_item, (list, UserList)):
            return rule_item in event_item
        else:
            return event_item == rule_item
