# -*- coding: utf-8 -*-
import urllib2
import re
import json
import os
import platform
import sys

class Web:
	def __init__(self):
		self.baseURL = u"http://www.enf.com.cn"
		self.fileName = "urls.json"

	def getCountryUrls(self):
		items = []
		collection = json.loads(open(self.fileName).read())
		directory  = collection.get("directory", "")
		countrys   = collection.get("countrys", [])
		products   = collection.get("products", "")
		types      = collection.get("type", "")
		for country in countrys:
			url = self.baseURL + "/" + directory + "/" + types + "/" + products + "/" + country
			print url
			if "/" in country:
				country = country.replace("/", "_")
			items.append({"country": country, "url": url})
		return items

class Hander:
	def __init__(self):
		self.userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
		self.baseURL   = u"http://www.enf.com.cn"
		self.reNextURL = '<a href="(.*?)" class="blackmid">(.*?)</a>'
		self.reCompany = 'itemprop="name">(.*?)</h1>'
		self.reAddress = 'itemprop="streetAddress">(.*?)</span>'
		self.reWebsite = '<a href="([a-zA-z]+://[^\s]*)" target="_blank" class="midtext" itemprop="url">'
		self.rePhone   = '(\+[\d|\s]{6,})'

	def getValue(self, list):
		if len(list) != 0:
			return list[0].strip()

	def getSendPhoneValue(self, list):
		if len(list) >= 2:
			return list[1].strip()

	def getRealUrl(self, str):
		urlStr = self.baseURL + str
		return urlStr.replace('amp;', '') 

	def doReq(self, url):
		unicodePage = None
		try:
			headers = {'User-Agent': self.userAgent}
			request = urllib2.Request(url, headers=headers)
			myResp  = urllib2.urlopen(request)
			myPage  = myResp.read()
			unicodePage = myPage.decode("utf-8")
		except urllib2.HTTPError,e:
			print "HTTPError !!!", e.code, e.reason
			print "----------------"
			print url
			print "----------------"
			pass
		except urllib2.URLError, e:
			print "URLError !!! ", e.reason
			print "----------------"
			print url
			print "----------------"
			pass
		return unicodePage

	def getSinglePageInfo(self, url):
		infoItem = {'company': '', 'address':'' ,'website':'',\
					'phone':'', 'sendphone':'', 'email':''}
		pageInfo = self.doReq(url)
		companyList = re.findall(self.reCompany, pageInfo, re.S)
		addressList = re.findall(self.reAddress, pageInfo, re.S)
		websiteList = re.findall(self.reWebsite, pageInfo, re.S)
		phoneList   = re.findall(self.rePhone  , pageInfo, re.S)
		infoItem['company'] = self.getValue(companyList)
		infoItem['address'] = self.getValue(addressList)
		infoItem['website'] = self.getValue(websiteList)
		infoItem['phone']   = self.getValue(phoneList)
		infoItem['sendphone'] = self.getSendPhoneValue(phoneList)
		return infoItem

	def getCountryCompanyUrlCollection(self, countryUrl):
		items = {"country": countryUrl["country"],"companyUrl": []}
		page = self.doReq(countryUrl["url"])
		if page is None:
			pass
		else:
			companyUrlItems = re.findall(self.reNextURL, page, re.S)
			for item in companyUrlItems:
				if u"</li>" not in item[0]:
					realUrl = self.getRealUrl(item[0])
					items["companyUrl"].append(realUrl)
		print items["country"]
		print len(items["companyUrl"])
		return items

	def getCompanyInfoCollection(self, countryUrl):
		countryCompanyUrls = self.getCountryCompanyUrlCollection(countryUrl)
		items = []
		for url in countryCompanyUrls["companyUrl"]:
			items.append(self.getSinglePageInfo(url))
		return items

class  Capsule(object):

	def collect(self, web, hander):
		countryUrls = web.getCountryUrls()
		for country in countryUrls:
			print "-----------------,", country["country"], "-------------------"
			print country
			items = hander.getCompanyInfoCollection(country)
			print items
		
class Spider:
	def __init__(self):
		self.web = Web()
		self.hander = Hander()
		self.capsule = Capsule()

	def grab(self):
		self.capsule.collect(self.web, self.hander)

spider = Spider()
spider.grab()




















