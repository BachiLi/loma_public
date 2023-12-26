class Subscriptable(type):
    caches = {}

    def __getitem__(self, arg):
        if (self, arg) not in self.caches:
            self.caches[(self, arg)] = type(self.__name__, (), {'subscript': arg})
        return self.caches[(self, arg)]

class Input(metaclass = Subscriptable): pass
class Output(metaclass = Subscriptable): pass
class Array(metaclass = Subscriptable): pass
