import logging
from termcolor import colored

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors
    from : https://stackoverflow.com/questions/1343227/can-pythons-logging-format-be-modified-depending-on-the-message-log-level
    """
    format_strings = {
        logging.DEBUG: colored("[%(asctime)s.%(msecs)03d][%(levelname)s][%(filename)s:%(lineno)d] %(message)s", color='cyan',attrs=['bold']),
        logging.INFO: colored("[%(asctime)s.%(msecs)03d][%(levelname)s][%(filename)s:%(lineno)d] %(message)s", color='white'),
        logging.WARNING: colored("[%(asctime)s.%(msecs)03d][%(levelname)s][%(filename)s:%(lineno)d] %(message)s", color='yellow'),
        logging.ERROR: colored("[%(asctime)s.%(msecs)03d][%(levelname)s][%(filename)s:%(lineno)d] %(message)s", color='red'),
        logging.CRITICAL: colored("[%(asctime)s.%(msecs)03d][%(levelname)s][%(filename)s:%(lineno)d] %(message)s", color='white',on_color='on_red')
    }
    def format(self, record):
        log_fmt = self.format_strings.get(record.levelno)
        formatter = logging.Formatter(log_fmt,datefmt='%H:%M:%S')
        return formatter.format(record)

def create_logger(log_name : str, log_level : int) -> logging.Logger:
    log = logging.getLogger(log_name)
    log.setLevel(log_level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(CustomFormatter())
    log.addHandler(console_handler)
    return log