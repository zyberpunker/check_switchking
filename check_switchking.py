#!/usr/bin/python

import urllib2
from xml.dom.minidom import parseString
import pynagios 
from pynagios import Plugin, make_option
import sys

username = ""
password = ""


class switchking(Plugin):
	id = make_option("-i","--id", dest="id", type="int")
	unit = make_option("-u","--unit", dest="unit",type="int", help="1=temp, 2=humidity")
	devicetype = make_option("-d","--device", dest="device", type="int", help="1=datasource (default), 2=device")

	def check(self):
		if self.options.devicetype == 2:
		  return self.device()
		else:
		  return self.datasource()	

	def datasource(self):
	
		hostname = self.options.hostname
		id = self.options.id
		unit = self.options.unit
	
		# Authentication
		auth_handler = urllib2.HTTPBasicAuthHandler()
		auth_handler.add_password(realm='',
	                          uri="http://%s:8800/datasources/%s" % (hostname, id),
        	                  user="%s" % username,
                	          passwd="%s" % password)
		opener = urllib2.build_opener(auth_handler)
		# install auth to use with urlopen

		urllib2.install_opener(opener)

		file = urllib2.urlopen("http://%s:8800/datasources/%s" % (hostname, id))
		return_str = file.read()
	
		dom = parseString(return_str)
		xmlTag = dom.getElementsByTagName('LastValue')[0].toxml()
		xmlData=xmlTag.replace('<LastValue>','').replace('</LastValue>','')
		xmlTag = dom.getElementsByTagName('Name')[0].toxml()
                xmlName=xmlTag.replace('<Name>','').replace('</Name>','')

		# Replace , with .
		xmlData=xmlData.replace( ",",".")
		value=float(xmlData)

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
		  sys.exit()
	        return result 


        def device(self):
		id = self.options.id
                hostname = self.options.hostname

		# Authentication
                auth_handler = urllib2.HTTPBasicAuthHandler()
                auth_handler.add_password(realm='',
                                  uri="http://%s:8800/devices/%s" % (hostname, id),
                                  user="%s" % username,
                                  passwd="%s" % password)
                opener = urllib2.build_opener(auth_handler)
                # install auth to use with urlopen

                urllib2.install_opener(opener)
                file = urllib2.urlopen("http://%s:8800/devices/%s" % (hostname, id))
                return_str = file.read()

                dom = parseString(return_str)
                xmlTag = dom.getElementsByTagName('CurrentDimLevel')[0].toxml()
                xmlData=xmlTag.replace('<CurrentDimLevel>','').replace('</CurrentDimLevel>','')
                xmlTag = dom.getElementsByTagName('Name')[0].toxml()
                xmlName=xmlTag.replace('<Name>','').replace('</Name>','')

                # Replace , with .
#                xmlData=xmlData.replace( ",",".")
                value=float(xmlData)

                finaloutput = "%s is %s" % (xmlName, value)

                # Return a response for that value
                result = self.response_for_value(value, message=finaloutput)
                result.set_perf_data("Value", value,warn=self.options.warning,crit=self.options.critical)
                return result


if __name__ == "__main__":
      switchking().check().exit()

