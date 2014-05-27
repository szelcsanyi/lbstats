#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Loadbalancer Statistics Monitor Daemon
 Collects request via syslog from loadbalancer
 and generates real-time statistics from them
 which are accessible over an http interface.
"""

from daemon import runner
import sys

import config

from lbstats.daemon import LoadbalancerStatisticsMonitorDaemon
from lbstats.log import init_log

if __name__ == '__main__':

	logger, loghandler = init_log(config.MONITOR_LOGFILE, 'loadbalancer_statistics_monitor')

	app = LoadbalancerStatisticsMonitorDaemon()

	try:
		daemon_runner = runner.DaemonRunner(app)
		daemon_runner.daemon_context.files_preserve=[loghandler.stream]
		daemon_runner.do_action()
	except Exception, e:
		print "Not running"
		print e
		sys.exit(1)


	logger.info("Exiting")
