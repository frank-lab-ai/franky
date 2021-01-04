from functools import wraps
from typing import Any, Union, Optional
from collections.abc import Callable
from abc import ABC, abstractmethod
from os import path, makedirs
import pickle
import hashlib

DATA_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '../data/kb')
makedirs(DATA_DIRECTORY, exist_ok=True)


class KB:

    def __init__(self, name: str):
        self.name = name

    @classmethod
    def memoize(cls, key_generator: Optional[Union[Callable, str]] = None):
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                key = key_generator(
                    *args, **kwargs) if callable(key_generator) else key_generator
                keys = [hashlib.md5(str.encode(self.name)
                                    ).hexdigest(), func.__name__]

                if key:
                    keys.append(key)

                filename = '_'.join(keys)
                filepath = path.join(DATA_DIRECTORY, filename)

                if (path.exists(filepath)):
                    with open(filepath, 'rb') as f:
                        return pickle.load(f)
                else:
                    result = func(self, *args, **kwargs)
                    with open(filepath, 'wb') as f:
                        pickle.dump(result, f)
                    return result

            return wrapper
        return decorator

    @abstractmethod
    def get_entities(self):
        raise NotImplementedError

    @abstractmethod
    def get_relationships(self):
        raise NotImplementedError
