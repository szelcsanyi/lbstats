# -*- coding: utf-8 -*-

import logging
import logging.handlers

def init_log(logfile, loggerName):
	logger = logging.getLogger(loggerName)
	loghandler = logging.handlers.RotatingFileHandler(logfile, maxBytes=10000000, backupCount=3)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	loghandler.setFormatter(formatter)
	logger.addHandler(loghandler)
	logger.setLevel(logging.INFO)
	return logger, loghandler
