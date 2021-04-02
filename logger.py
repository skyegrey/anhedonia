import datetime


class FileLogger:
    def __init__(self, filename):
        self.filename = filename

    def send_to_logger(self, level, message):
        logger.log(level, self.filename, message)

    def trace(self, message):
        self.send_to_logger('TRACE', message)

    def info(self, message):
        self.send_to_logger('INFO', message)


class Logger:

    def __init__(self, log_directory):
        self.file_loggers = {}
        start_date = datetime.datetime.now()
        year, month, date, time = start_date.year, start_date.month, start_date.day, start_date.time()
        self.file = open(f'{log_directory}/[{year}-{month}-{date}@{time.hour}:{time.minute}].log', 'w')

        self.do_print = True

    def get_logger(self, filename):
        self.file_loggers[filename] = FileLogger(filename)
        return self.file_loggers[filename]

    def log(self, level, filename, message):
        time = datetime.datetime.now()
        hour, minute, second = time.hour, time.minute, time.second
        log_line = f'[{hour}:{minute}:{(2 -  len(str(second)))* "0" + str(second)}][{level}][{filename}]{message}'
        self.file.write(log_line)
        if self.do_print:
            print(log_line)


logger = Logger('logs')
