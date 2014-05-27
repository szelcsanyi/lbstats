# -*- coding: utf-8 -*-

import threading
import os, pwd, grp, sys
import time
import logging
import config
import inspect

class SimpleDaemon(object):
	def __init__(self):
		self.stdin_path = '/dev/null'
		self.stdout_path = '/dev/null'
		self.stderr_path = '/dev/null'
		self.pidfile_timeout = 5
		self.working_directory = os.getcwd()

	def dropPrivileges(self):
		if os.getuid() == 0:
			gid=grp.getgrnam('nogroup').gr_gid
			uid=pwd.getpwnam('nobody').pw_uid
			if os.path.isfile(self.logfile):
				os.chown(self.logfile, uid, gid)
			if os.path.isfile(self.logfile):
				os.chown(self.logfile, uid, gid)
			if os.path.isfile(self.logfile + '.lock'):
				os.chown(self.logfile + '.lock', uid, gid)
			os.setgroups([])
			os.setgid(gid)
			os.setuid(uid)

		os.chdir(self.working_directory)

	def run(self):
		return


class LoadbalancerStatisticsCollectorDaemon(SimpleDaemon):
	
	def __init__(self):
		SimpleDaemon.__init__(self)

		from lbstats.requests import CollectorRequests
		self.logfile = config.COLLECTOR_LOGFILE
		self.logger = logging.getLogger('loadbalancer_statistics_collector')
		self.pidfile_path =  config.COLLECTOR_PIDFILE
		self.requests = CollectorRequests(config.COLLECTOR_REMOTE_HOST, config.COLLECTOR_REMOTE_PORT)
		self.start_time = 0

	def run(self):
		try:
			self.logger.info("Starting collector")

			# syslog collector thread
			from lbstats.syslog import syslogCollectorUDPServer
			syslog_handler = syslogCollectorUDPServer(config.COLLECTOR_DATA_HOST, config.COLLECTOR_DATA_PORT, self.requests)
			syslog_thread = threading.Thread(name='SyslogServer', target=syslog_handler.serve_forever )
			syslog_thread.setDaemon(True)
			syslog_thread.start()
			self.logger.info('Syslog collector server loop running in thread:' + syslog_thread.getName())

			self.dropPrivileges()

			self.start_time = time.time()
			while True:
				if time.time() - self.start_time > 1:
					self.start_time=time.time()
					self.requests.sendAggregatedRequests()
				time.sleep(1)

		except Exception, e:
			self.logger.exception(e)


class LoadbalancerStatisticsMonitorDaemon(SimpleDaemon):
	
	def __init__(self):
		SimpleDaemon.__init__(self)

		from lbstats.requests import AggregatedRequests
		self.logfile = config.MONITOR_LOGFILE
		self.logger = logging.getLogger('loadbalancer_statistics_monitor')
		self.pidfile_path =  config.MONITOR_PIDFILE
		self.requests = AggregatedRequests(config.MAX_MEASURE_TIME, config.MAX_REQUESTS, config.TOP_REQUEST_COUNT, config.RPS_HISTORY)
		self.start_time = 0

	def run(self):
		try:
			self.logger.info("Starting monitor")

			# http thread
			from lbstats.http import httpServer
			http_handler = httpServer(config.MONITOR_HTTP_HOST, config.MONITOR_HTTP_PORT, self.requests)
			http_thread = threading.Thread(name='HttpServer', target=http_handler.start)
			http_thread.setDaemon(True)
			http_thread.start()
			self.logger.info('Http server loop running in thread:' + http_thread.getName())

			# syslog collector thread
			from lbstats.syslog import syslogMonitorUDPServer
			syslog_handler = syslogMonitorUDPServer(config.MONITOR_DATA_HOST, config.MONITOR_DATA_PORT, self.requests)
			syslog_handler.max_packet_size = 65535
			syslog_thread = threading.Thread(name='SyslogServer', target=syslog_handler.serve_forever )
			syslog_thread.setDaemon(True)
			syslog_thread.start()
			self.logger.info('Syslog monitor server loop running in thread:' + syslog_thread.getName())

			self.dropPrivileges()

			self.start_time = time.time()
			while True:
				if time.time() - self.start_time > 1:
					self.start_time=time.time()
					self.requests.cleanupRequests()
					self.requests.reqPerSecCollector()
				time.sleep(1)

		except Exception, e:
			self.logger.exception(e)