# -*- coding: utf-8 -*-

import SocketServer
#import re

collector_requests = None
monitor_requests = None

"""
Simple udp socket server for collecting syslog messages
"""
def syslogCollectorUDPServer(host, port, req):
	global collector_requests
	collector_requests = req
	return SocketServer.UDPServer((host, port), syslogCollectorUDPHandler )

class syslogCollectorUDPHandler(SocketServer.BaseRequestHandler):
 
	def __init__(self, request, client_address, server):
		SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
		return

	def handle(self):
		data = bytes.decode(self.request[0].strip())
		if data[0] == '<':
			pos = data.find("stats:")
			if pos > 0:
				request_info = data[pos+6:].lstrip().split(' ')
				collector_requests.addRequest(request_info[0], request_info[1], request_info[2], request_info[4] )


"""
Simple udp socket server for receiving aggregated statistics
"""
def syslogMonitorUDPServer(host, port, req):
	global monitor_requests
	monitor_requests = req
	return SocketServer.UDPServer((host, port), syslogMonitorUDPHandler )

class syslogMonitorUDPHandler(SocketServer.BaseRequestHandler):
 
	def __init__(self, request, client_address, server):
		SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
		return

	def handle(self):
		monitor_requests.addRequest( self.client_address[0], self.request[0] )
