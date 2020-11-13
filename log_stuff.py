import logging
import sys

logging.basicConfig(stream=sys.stdout)

class Logger(type):
    def __init__(cls, *args):
        super().__init__(*args)

        # Explicit name mangling
        logger_attribute_name = '_' + cls.__name__ + '__logger'

        # Logger name derived accounting for inheritance for the bonus marks
        logger_name = '.'.join([c.__name__ for c in cls.mro()[-2::-1]])

        setattr(cls, logger_attribute_name, logging.getLogger(logger_name))

class Base(metaclass=Logger):
    def __init__(self):
        self.__logger.error('init base')

    def func_base(self):
        self.__logger.error('func base')


class Parent(Base):
    def func_parent(self):
        self.__logger.error('func parent')

p = Parent()
p.func_base()
p.func_parent()