# -*- coding: utf-8 -*-

from lxml import etree
import urllib


def get_ups_info(tracking_num):
	url = 'https://www.ups.com/WebTracking/processInputRequest?tracknum={0}&AgreeToTermsAndConditions=yes'.format(tracking_num)
	web = urllib.urlopen(url)
	s = web.read()
	html = etree.HTML(s)

	try:
		tr_nodes = html.xpath('//*[@id="fontControl"]/fieldset/div[3]/fieldset/div/fieldset/div/fieldset/div[1]/div[2]/fieldset/div[2]/table')

		header = [i[0].text for i in tr_nodes[0].xpath("tbody")]

		td_content = [[td.text for td in tr.xpath('td')] for tr in tr_nodes[1:]]

		status_arr = []

		for tr in html.xpath("//tr")[1]:
			print(tr)
			for td in tr.xpath("//td"):
				if isinstance(td.text, basestring):
					s = td.text.translate(None, '\t\n\r')
					s = s.lstrip()
					s = s.rstrip()
					status_arr.append(s)
	except IndexError:
		return ' UPS could not locate the shipment details for your request. Please verify your information and try again later.'
	return status_arr[0:4]

