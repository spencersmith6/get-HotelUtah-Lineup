from bs4 import BeautifulSoup
import urllib
from twilio.rest import TwilioRestClient

import argparse
import json


def getCredentials(file_name):
    with open(file_name, 'r') as f:
        credentials = f.read()
    return json.loads(credentials)


def sendText(credentials, text):
    # the following line needs your Twilio Account SID and Auth Token
    client = TwilioRestClient(credentials['twilio_sid'], credentials['twilio_token'])

    # change the "from_" number to your Twilio number and the "to" number
    # to the phone number you signed up for Twilio with, or upgrade your
    # account to send SMS to any phone number
    client.messages.create(to=credentials['your_phone#'], from_=credentials['twilio_phone#'],
                           body=text)


def getSched():
    SITE = 'http://www.hotelutah.com/'
    r = urllib.urlopen(SITE).read()
    soup = BeautifulSoup(r)
    sched = [i for i in soup.find_all('div', class_="list-view-item")]
    return sched



def getArtists(sched_raw):
    schedule_list = []
    for i in sched_raw:
        event = i.find_all('h1')
        date= i.find_all('h2', class_='dates')[0].get_text()
        schedule_list.append( (date, [event[x].get_text() for x in range(len(event )) ] ))

    artists = [i[1] for i in schedule_list]

    return artists, [item for sublist in artists for item in sublist]


def create_text(schedule_list):
    tmp = [x[0] + ':\n' + '\n'.join([i for i in x[1]]) for x in schedule_list]
    text = '\n\n'.join(tmp) + '\n'
    return text


def main(args):
    creds = getCredentials(args.twil)
    sched_raw = getSched()
    artists, artists_flat = getArtists(sched_raw)
    print artists


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-twil", help="Twilio Credentials Filepath")
    args = parser.parse_args()
    main(args)



