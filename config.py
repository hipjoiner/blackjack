from datetime import datetime, timedelta
from inspect import signature


home_dir = 'C:/Users/John/blackjack'
card_symbols = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A', 'x']
card_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 0]
card_indexes = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'A': 9, 'x': 10}


class CachedInstance(type):
    """For unique instances of a class by calling args.
        class X(metaclass=CachedInstance):
            def __init__(self, vara, varb):
                self.vara = vara
                self.varb = varb
            etc.
        Treat all named arguments correctly, whether positional or explicitly named in the instantiation call.
        Ref: https://stackoverflow.com/questions/50820707/python-class-instances-unique-by-some-property
    """
    def __call__(cls, *args, **kwargs):
        """Use inspection to form an explicit dict of args by name,
           whether those args are supplied positionally, or by name, or by default"""
        cls._instances = {}
        explicit_args = {}
        poppable_args = list(args)
        for name, parm in signature(cls.__init__).parameters.items():
            if name == 'self':
                continue
            if len(poppable_args):
                val = poppable_args.pop(0)
            elif name in kwargs:
                val = kwargs[name]
            else:
                val = parm.default
            explicit_args[name] = val
        # Class itself plus explicit dict of args in alpha order form a key defining uniqueness of object
        # index = cls, tuple(sorted(explicit_args.items()))
        index = tuple(sorted(explicit_args.items()))
        if index not in cls._instances:
            cls._instances[index] = super(CachedInstance, cls).__call__(*args, **kwargs)
        return cls._instances[index]


def log(txt):
    now = datetime.now()
    print(f'{now.strftime("%Y-%m-%d %H:%M:%S")} {txt}')


def log_occasional(txt, seconds=3):
    now = datetime.now()
    if not hasattr(log_occasional, 'last_time'):
        log_occasional.last_time = now - timedelta(days=1)
    if now > log_occasional.last_time + timedelta(seconds=seconds):
        log(txt)
        log_occasional.last_time = now
