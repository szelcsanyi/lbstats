# -*- coding: utf-8 -*-

from bottle import template, request, redirect, Bottle
import json

class httpServer():
	def __init__(self, host, port, requests):
		self.app = Bottle()
		self.host = host
		self.port = port
		self.requests = requests
		self.route()
	
	def start(self):
		self.app.run(host=self.host, port=self.port, debug=True, quiet=True)

	def route(self):
		self.app.route('/', method="GET", callback=self.redirectToMain)
		self.app.route('/lbstats', method="GET", callback=self.redirectToMain)
		self.app.route('/lbstats/map', method="GET", callback=self.showMap)
		self.app.route('/lbstats/details', method="GET", callback=self.showDetails)
		self.app.route('/lbstats/', method="GET", callback=self.showOverview)
		self.app.route('/lbstats/ips', method="GET", callback=self.urlsByIP)
		self.app.route('/lbstats/urls', method="GET", callback=self.ipsByUrl)
		self.app.route('/lbstats/all', method="GET", callback=self.all)
		self.app.route('/lbstats/getreqpshistory', method="GET", callback=self.getReqPSHistory)
		self.app.route('/lbstats/gettopdomains', method="GET", callback=self.getTopDomains)
		self.app.route('/lbstats/gettopcountries', method="GET", callback=self.getTopCountries)
		self.app.route('/lbstats/getcounters', method="GET", callback=self.getCounters)
		self.app.error_handler = { 404: self.error404 }

	def error404(self, error):
		return 'Not Found'

	def redirectToMain(self):
		redirect("/lbstats/")

	def urlsByIP(self):
		ip = request.query.ip
		host = request.query.host
		group = request.query.group
		if ip and host and group:
			return template('./templates/modal_list', items=self.requests.getCommonUrlsByIP(group, host, ip) )
		else:
			return "No ip, host or group given!"

	def ipsByUrl(self):
		url = request.query.url
		host = request.query.host
		group = request.query.group
		if url and host and group:
			return template('./templates/modal_list', items=self.requests.getCommonIpsByUrl(group, host, url) )
		else:
			return "No url, host or group given!"


	def all(self):
		response ="<p>Urls:</p><table>"
		for i in self.requests.getRequests():
			response += "<tr><td> %s </td></tr>" % i
		response += "</table>"
		return response

	def getCounters(self):
		counters = {}
		counters['requests'] = self.requests.getCachedCount()
		counters['reqps'] = self.requests.getReqPerSec()
		return json.dumps(counters)

	def getReqPSHistory(self):
		group = request.query.group
		history_length=300 if group else 180
		history = self.requests.getReqPerSecHistory(history_length, group)
		keys = sorted( history )
		if len(keys):
			reqpshistory = [ ['sec'] + keys ]
			for i in range(history_length):
				row = [i]
				for h in keys:
					row.append( history[h][i] )
				reqpshistory.append(row)
			return json.dumps( reqpshistory )
		else:
			return json.dumps( [ ['sec', 'req'],[0, 0] ] )

	def getTopDomains(self):
		domains = [ ['Domain', 'Requests'] ]
		for domain in self.requests.getHostsByUsage():
			domains.append( [domain[0], domain[1]] )
		return json.dumps( domains )

	def getTopCountries(self):
		group = request.query.group
		countries = [ ['Country', 'Requests'] ]
		for country in self.requests.getCountries(group):
			countries.append( [country[0][1], country[1]] )
		return json.dumps( countries )

	def showOverview(self):
		return template('./templates/overview')

	def showMap(self):
		group = request.query.group
		if not group:
			group = 'all' 
		return template('./templates/map', group=group)

	def showDetails(self):
		group = request.query.group

		if group:
			stats = {}

			if self.requests.getCachedCount():
				for host in self.requests.getHosts(group):
					stats[host] = {}
					stats[host]['urls'] = self.requests.getCommonUrls(group, host)
					stats[host]['ips'] = self.requests.getCommonIPs(group, host)
					stats[host]['countries'] = self.requests.getCommonCountries(group, host)

			return template('./templates/groupdetails', stats=stats, group=group )
		else:
			return template('./templates/details', groups=self.requests.getGroups() )
