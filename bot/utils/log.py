import logging
import sys

fileHandler = logging.FileHandler("./data/logs.log", mode='a')
fileHandler.setFormatter(
    logging.Formatter(
        "[%(asctime)s %(name)s]: %(message)s", "%Y-%m-%d %H:%M:%S"
    )
)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(
    logging.Formatter(
        "[%(asctime)s %(name)s]: %(message)s", "%Y-%m-%d %H:%M:%S"
    )
)


def get_logger(file: str) -> logging.Logger:
    logger = logging.getLogger(file)
    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)
    return logger


def retrieve_logs(log_file: str, date: str):
    return [line.strip() for line in open(log_file, 'r') if line[1:11] == date]
