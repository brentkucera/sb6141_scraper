# this script parses data from the downstream section of the SB6141 modem's signal page and prints it
# the idea is to have a scheduled task run this script and append its output to a log file

from lxml import html
import requests
import string
import time

dnStream = {'channel_id': 0,
            'snr': 0,
            'power': 0}

dnStreams = []
column = 0
section = ""

now = time.time()

page = requests.get('http://192.168.100.1/cmSignalData.htm')
tree = html.fromstring(page.content)

centers = tree.xpath('//center')

for center in centers:
    if len(center.xpath('.//table/tbody/tr/th/font[text()="Downstream "]')) > 0:
        tds = center.xpath('./table/tbody/tr/td')
        for td in tds:
            if all(x.isalpha() or x.isspace() for x in td.text):
                if td.text == "Channel ID" or td.text == "Signal to Noise Ratio" or td.text == "Power Level":
                    section = td.text
                else:
                    section = ""

                column = 0
                continue

            elif all(x.isalnum() or x.isspace() or x == '-' for x in td.text):
                if section == "Channel ID":
                    dnStream['channel_id'] = int(td.text.strip())
                    dnStreams.append(dnStream.copy())
                elif section == "Signal to Noise Ratio":
                    dnStreams[column]['snr'] = int(td.text.strip().split()[0])
                    column += 1
                elif section == "Power Level":
                    dnStreams[column]['power'] = int(td.text.strip().split()[0])
                    column += 1

for item in dnStreams:
    print str(now) + "," + str(item['channel_id']) + "," + str(item['snr']) + "," + str(item['power'])

