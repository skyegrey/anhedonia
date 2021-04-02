import datetime


class FileLogger:
    def __init__(self, filename):
        self.filename = filename

    @staticmethod
    def info(message):
        logger.log('INFO', message)


class Logger:

    def __init__(self, log_directory):
        self.file_loggers = {}
        start_date = datetime.datetime.now()
        year, month, date, time = start_date.year, start_date.month, start_date.day, start_date.time()
        self.file = open(f'{log_directory}/[{year}-{month}-{date}@{time.hour}:{time.minute}].log', 'w')

    def get_logger(self, filename):
        self.file_loggers[filename] = FileLogger(filename)
        return self.file_loggers[filename]

    def log(self, level, message):
        time = datetime.time
        self.file.write(f'{str(time)}:{level}:{message}')


logger = Logger('logs')
