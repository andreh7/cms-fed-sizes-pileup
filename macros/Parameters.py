#!/usr/bin/env python

# helper class to allow pickling parameters

class Parameters(object):

    # see http://stackoverflow.com/questions/6313421/can-i-mark-variables-as-transient-so-they-wont-be-pickled
    # on how to make certain fields transient for pickling
    def __getstate__(self):
        state = dict(self.__dict__)
        
        # exclude modules and functions
        for key in state.keys():
            import types
            if isinstance(state[key], types.ModuleType):
                del state[key]
                continue

            if hasattr(state[key], '__call__'):
                del state[key]
                continue

        return state



    pass


