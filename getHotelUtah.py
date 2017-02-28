from bs4 import BeautifulSoup
import urllib
# we import the Twilio client from the dependency we just installed
from twilio.rest import TwilioRestClient
import csv
import sys


with open(sys.argv[1], 'r') as f:
    credentials = f.readline().split(',')

print credentials[1]
print credentials

SITE = 'http://www.hotelutah.com/'
r = urllib.urlopen(SITE).read()
soup = BeautifulSoup(r)


sched = [i for i in soup.find_all('div', class_="list-view-item")]

schedule_list = []
for i in sched:
    event = i.find_all('h1')
    date= i.find_all('h2', class_='dates')[0].get_text()
    schedule_list.append( (date, [event[x].get_text() for x in range(len(event )) ] ))

tmp = [x[0] + ':\n' + '\n'.join([i for i in x[1]]) for x in schedule_list]
text = '\n\n'.join(tmp)

# the following line needs your Twilio Account SID and Auth Token
client = TwilioRestClient(credentials[0], credentials[1])

# change the "from_" number to your Twilio number and the "to" number
# to the phone number you signed up for Twilio with, or upgrade your
# account to send SMS to any phone number
client.messages.create(to=credentials[2], from_=credentials[3],
                       body=text)

