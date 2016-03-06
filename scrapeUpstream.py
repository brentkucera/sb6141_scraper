# this script parses data from the upstream section of the SB6141 modem's signal page and prints it
# the idea is to have a scheduled task run this script and append its output to a log file

from lxml import html
import requests
import string
import time

upStream = {'channel_id': 0,
            'power': 0,
            'ranging': ""}

upStreams = []
column = 0
section = ""

now = time.time()

page = requests.get('http://192.168.100.1/cmSignalData.htm')
tree = html.fromstring(page.content)

centers = tree.xpath('//center')

for center in centers:
    if len(center.xpath('.//table/tbody/tr/th/font[text()="Upstream "]')) > 0:
        tds = center.xpath('./table/tbody/tr/td')
        for td in tds:
            # section != "Ranging Status " is a hack because that section doesn't have both numbers and
            # letters in it all the time and I don't know what values it can have anyway. It's the last
            # section so I can get away with doing this
            if all(x.isalpha() or x.isspace() for x in td.text) and section != "Ranging Status ":
                if td.text == "Channel ID" or td.text == "Power Level" or td.text == "Ranging Status ":
                    section = td.text
                else:
                    section = ""

                column = 0
                continue
            elif all(x.isalnum() or x.isspace() or x in string.punctuation for x in td.text):
                if section == "Channel ID":
                    upStream['channel_id'] = int(td.text.strip())
                    upStreams.append(upStream.copy())
                elif section == "Power Level":
                    upStreams[column]['power'] = int(td.text.strip().split()[0])
                    column += 1
                elif section == "Ranging Status ":
                    upStreams[column]['ranging'] = td.text.strip()
                    column += 1



for item in upStreams:
    print str(now) + "," + str(item['channel_id']) + "," + str(item['power']) + "," + item['ranging']