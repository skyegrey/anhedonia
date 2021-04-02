from logger import logger


def initializer_logger(initializer):

    def wrapper(self, *args):
        self.logger.trace(f'Initializing {self.__class__.__name__}')
        initializer(self, *args)
        self.logger.trace(f'Initialized {self.__class__.__name__}')

    return wrapper


def class_function_logger(function):

    def wrapper(self, *args):
        self.logger.trace(f'Entering function {function.__name__}')
        result = function(self, *args)
        self.logger.trace(f'Exiting function {function.__name__}')
        return result

    return wrapper


def class_logger(class_reference):
    log = logger.get_logger(class_reference.__name__)
    class_reference.logger = log
    return class_reference
