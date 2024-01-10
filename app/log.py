import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def getConsoleHandler():
	consoleHandler = logging.StreamHandler(sys.stdout)
	consoleHandler.setFormatter(FORMATTER)
	return consoleHandler

#Created path if doesnt exists
#Rotates log every night
def getFileHandler(logPath):
	os.makedirs(os.path.dirname(logPath), exist_ok=True)
	file_handler = TimedRotatingFileHandler(logPath, when='midnight', encoding='utf-8')
	file_handler.setFormatter(FORMATTER)
	return file_handler


def getLogger(loggerName, logPath):
	logger = logging.getLogger(loggerName)

	logger.addHandler(getConsoleHandler())
	logger.addHandler(getFileHandler(logPath))

	# with this pattern, it's rarely necessary to propagate the error up to parent
	logger.propagate = False

	return logger