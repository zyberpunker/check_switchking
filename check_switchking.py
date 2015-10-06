#!/usr/bin/python
# coding=utf-8

##################################################################
# (c) by Ola Sandström, https://github.com/zyberpunker
#
# 
# 0.1 | First edition
# 0.2 | Modified by Mattias Bergsten to handle Switch King on Mono on Linux
# 0.3 | Now prints nice help text if you do something wrong
#
##################################################################
import urllib2
from xml.dom.minidom import parseString
import pynagios 
from pynagios import Plugin, make_option
import sys
import base64

class PreemptiveBasicAuthHandler(urllib2.HTTPBasicAuthHandler):
    '''Preemptive basic auth.

    Instead of waiting for a 401 to then retry with the credentials,
    send the credentials if the url is handled by the password manager.
    Note: please use realm=None when calling add_password.'''
    def http_request(self, req):
        url = req.get_full_url()
        realm = None
        # this is very similar to the code from retry_http_basic_auth()
        # but returns a request object.
        user, pw = self.passwd.find_user_password(realm, url)
        if pw:
	    raw = "%s:%s" % (user, pw)
            auth = 'Basic %s' % base64.b64encode(raw).strip()
            req.add_unredirected_header(self.auth_header, auth)
        return req

    https_request = http_request

username = "user"
password = "pass"

class switchking(Plugin):
	apiid = make_option("-i","--id", dest="apiid", type="int")
	unit = make_option("-u","--unit", dest="unit",type="int", help="1=temp, 2=humidity")
	devicetype = make_option("-d","--device", dest="device", type="int", help="1=datasource (default), 2=device")

	def check(self):
		# pynagios uses optparse. optparse doesn't have required arguments. blah.
		if self.options.apiid == None:
			self._option_parser.print_help()
			sys.exit(2)
		elif self.options.unit == None:
			self._option_parser.print_help()
			sys.exit(2)
		elif self.options.devicetype == 2:
		  return self.devices()
		else:
		  return self.datasource()	

	def datasource(self):
		unit = self.options.unit
		hostname = self.options.hostname
		apiid = self.options.apiid

		# Authentication
		auth_handler = PreemptiveBasicAuthHandler()
		auth_handler.add_password(
			realm=None,
			uri="http://%s:8800/datasources/%s" % (hostname, apiid),
			user="%s" % username,
			passwd="%s" % password)
		opener = urllib2.build_opener(auth_handler)
		# install auth to use with urlopen

		urllib2.install_opener(opener)

		file = urllib2.urlopen("http://%s:8800/datasources/%s" % (hostname, apiid))
		return_str = file.read()
	
		dom = parseString(return_str)
		xmlTag = dom.getElementsByTagName('LastValue')[0].toxml()
		xmlData = xmlTag.replace('<LastValue>','').replace('</LastValue>','')
		xmlTag = dom.getElementsByTagName('Name')[0].toxml()
		xmlName = xmlTag.replace('<Name>','').replace('</Name>','')

		# Replace , with .
		xmlData = xmlData.replace( ",",".")
		value = float(xmlData)

		if unit == 1:
			finaloutput = "%s is %s" % (xmlName, value)
			result = self.response_for_value(value, message=finaloutput)
			result.set_perf_data("Value", value,warn=self.options.warning,crit=self.options.critical)
		elif unit == 2:
			unit = "%"
			finaloutput = "%s is %s%s" % (xmlName, value, unit)
			result = self.response_for_value(value, message=finaloutput)
			result.set_perf_data("Value", value,uom=unit,warn=self.options.warning,crit=self.options.critical)
		else:
			print "wrong type"
			sys.exit(2)
		return result 


	def devices(self):
		apiid = self.options.apiid
		hostname = self.options.hostname
		apiid = self.options.apiid

		# Authentication
		auth_handler = PreemptiveBasicAuthHandler()
		auth_handler.add_password(
			realm=None,
			uri="http://%s:8800/devices/%s" % (hostname, apiid),
			user="%s" % username,
			passwd="%s" % password)
		opener = urllib2.build_opener(auth_handler)
		# install auth to use with urlopen

		urllib2.install_opener(opener)

		file = urllib2.urlopen("http://%s:8800/devices/%s" % (hostname, apiid))
		return_str = file.read()
	
		dom = parseString(return_str)
		xmlTag = dom.getElementsByTagName('CurrentDimLevel')[0].toxml()
		xmlData = xmlTag.replace('<CurrentDimLevel>','').replace('</CurrentDimLevel>','')
		xmlTag = dom.getElementsByTagName('Name')[0].toxml()
		xmlName = xmlTag.replace('<Name>','').replace('</Name>','')

		# Replace , with .
		xmlData=xmlData.replace( ",",".")
		value = float(xmlData)

		finaloutput = "%s is %s" % (xmlName, value)

		# Return a response for that value
		result = self.response_for_value(value, message=finaloutput)
		result.set_perf_data("Value", value,warn=self.options.warning,crit=self.options.critical)
		return result

if __name__ == "__main__":
	switchking().check().exit()
