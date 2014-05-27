# -*- coding: utf-8 -*-

from threading import Lock
from collections import Counter, deque
from zlib import compress, decompress
import string
import time
import logging
import socket
import pickle

class CollectorRequests:

	def __init__(self, remote_ip, remote_port):
		self.requests = {}
		self.request_count = 0
		self.remote_ip = remote_ip
		self.remote_port = remote_port
		self.lock = Lock()
		self.logger = logging.getLogger('loadbalancer_statistics_collector')


	def addRequest(self, group, ip, host, url):
		if self.request_count < 1000:
			url = url.split('?')[0]
			if host[0] == '{' and host[-1] == '}':
				host = host[1:-1]
			host = host.split(':')[0]
			self.lock.acquire()
			try:
				if not group in self.requests:
					self.requests[group]=deque()
				self.requests[group].append( ( ip, host, url ) )
				self.request_count += 1
			finally:
				self.lock.release()

			if self.request_count >= 500:
				self.sendAggregatedRequests()

	def sendAggregatedRequests(self):
		self.lock.acquire()
		try:
			if self.request_count > 0:
				self.logger.info("Sending %d items" % self.request_count ) 
				data = compress( pickle.dumps(self.requests), 6 )
				sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				sock.sendto(data, (self.remote_ip, self.remote_port))
				sock.close()
		finally:
			self.requests = {}
			self.request_count = 0
			self.lock.release()



class AggregatedRequests:

	def __init__(self, max_measure_time, max_requests, top_request_count, rps_history):
		self.max_measure_time = max_measure_time
		self.max_requests = max_requests
		self.top_request_count = top_request_count
		self.rps_history = rps_history
		self.requests = {}
		self.request_count = 0
		self.lock = Lock()
		self.reqps = 0
		self.reqps_per_group = {}
		self.reqps_history_store = {}
		self.logger = logging.getLogger('loadbalancer_statistics_monitor')

		try:
			import GeoIP
			self.gi = GeoIP.open("/usr/share/GeoIP/GeoIP.dat",GeoIP.GEOIP_MEMORY_CACHE)
		except Exception, e:
			self.logger.error("Geoip error: %s", e)
			self.gi = None


	def reqPerSecCollector(self):
		self.lock.acquire()
		try:
			delete_empty_group = []
			reqps = 0

			for group,v in self.reqps_per_group.iteritems():
				if group not in self.reqps_history_store:
					self.reqps_history_store[group] = deque([], self.rps_history )
				self.reqps_history_store[group].append( v )
				reqps += v

			for group in self.reqps_history_store:
				if group not in self.reqps_per_group:
					self.reqps_history_store[group].append(0)
					if sum( self.reqps_history_store[group] ) == 0:
						delete_empty_group.append(group)

			for i in delete_empty_group:
				del self.reqps_history_store[i]
			
			self.reqps_per_group = {}
			self.reqps = reqps

		except Exception, e:
			self.logger.exception(e)
		finally:
			self.lock.release()


	def addRequest(self, ip, data):
		try:
			new_requests = pickle.loads( decompress(data) )
		except Exception, e:
			self.logger.exceptin(e)
			return

		new_requests_count = 0

		self.lock.acquire()
		try:
			for group,v in new_requests.iteritems():
				new_requests_count += len(v)
				if group not in self.requests:
					self.requests[group] = deque([], self.max_requests )
				if group not in self.reqps_per_group:
					self.reqps_per_group[group] = 0
				for i in v:
					self.requests[group].append( ( int(time.time()), i ) )
					self.reqps_per_group[group] += 1

			self.logger.info("Received %d requests from %s" % (new_requests_count, ip) )
		except Exception, e:
			self.logger.exception(e)
		finally:
			self.lock.release()

	def cleanupRequests(self):
		empty_groups = []
		request_count = 0
		time_limit = time.time() - self.max_measure_time

		self.lock.acquire()
		try:
			for group,v in self.requests.iteritems():

				while len(v) and v[0][0] < time_limit:
					v.popleft()

				if len(v) == 0:
					empty_groups.append(group)
			
				request_count += len(v)

			self.request_count = request_count

			for group in empty_groups:
				del self.requests[group]

		except Exception, e:
			self.logger.exception(e)
		finally:
			self.lock.release()


	def getBufferTime(self):
		return self.max_measure_time

	def getReqPerSec(self):
		return self.reqps

	def getReqPerSecHistory(self, interval, group=None):
		history = {}
		if interval <= self.rps_history:
			self.lock.acquire()
			try:
				if group:
					history[group] = ( [0] * (interval - len(self.reqps_history_store[group])) ) + list(self.reqps_history_store[group])[-interval:]
				else:
					for group in self.reqps_history_store:
						history[group] = ( [0] * (interval - len(self.reqps_history_store[group])) ) + list(self.reqps_history_store[group])[-interval:]
			except Exception, e:
				self.logger.exception(e)
			finally:
				self.lock.release()

		return history


	def getCachedCount(self):
		return self.request_count

	def getHosts(self, group):
		hosts = set()
		for i in list(self.requests[group]):
			hosts.add(i[1][1])
		return list(hosts)

	def getGroups(self):
		return self.requests

	def getCommon(self, group, host, field):
		cnt = deque()
		self.lock.acquire()
		try:
			for i in self.requests[group]:
				if i[1][1] == host:
					cnt.append( i[1][field] )
		finally:
			self.lock.release()
		return Counter(cnt)

	def getCommonUrls(self, group, host):
		return self.getCommon(group, host, 2).most_common(self.top_request_count)

	def getCommonIPs(self, group, host):
		return self.getCommon(group, host, 0).most_common(self.top_request_count)
		
	def getCommonCountries(self, group, host):
		return self.getCountriesFromIPs(self.getCommon(group, host, 0)).most_common(self.top_request_count)
		
	def getCommonByCond(self, group, host, field, condField, condValue):
		cnt = deque()
		self.lock.acquire()
		try:
			for i in self.requests[group]:
				if i[1][condField] == condValue and i[1][1] == host:
						cnt.append( i[1][field] )
		finally:
			self.lock.release()
		return Counter(cnt).most_common(self.top_request_count)

	def getCommonIpsByUrl(self, group, host, url):
		return self.getCommonByCond(group, host, 0, 2, url)

	def getCommonUrlsByIP(self, group, host, ip):
		return self.getCommonByCond(group, host, 2, 0, ip)

	def getHostsByUsage(self):
		hosts = deque()
		self.lock.acquire()
		try:
			for group,v in self.requests.iteritems():
				for i in v:
					hosts.append( i[1][1] )
		finally:
			self.lock.release()
		return Counter(hosts).most_common(5)

	def getCountriesFromIPs(self, ips):
		countries = Counter()
		if self.gi:
			for i in ips.items():
				try:
					country_name = self.gi.country_name_by_addr( i[0] )
					country_code = self.gi.country_code_by_addr( i[0] )
					if country_name and country_code:
						countries[ ( unicode( country_name , errors='ignore'), unicode( country_code , errors='ignore') ) ] += i[1]
				except Exception, e:
					self.logger.error(e)
		return countries

	def getCountries(self, group):
		ips = deque()
		self.lock.acquire()
		if group == '':
			group = 'all'
		try:
			if group == 'all':
				for group,v in self.requests.iteritems():
					for i in v:
						ips.append( i[1][0] )
			else:
				for i in self.requests[group]:
					ips.append( i[1][0] )
		finally:
			self.lock.release()

		return self.getCountriesFromIPs( Counter(ips) ).items()

	def getRequests(self):
		urls = deque()
		self.lock.acquire()
		try:
			for k,v in self.requests.iteritems():
				for i in v:
					urls.append(i[1][1] + i[1][2])
		finally:
			self.lock.release()
		return urls
