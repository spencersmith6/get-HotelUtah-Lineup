from bs4 import BeautifulSoup
import urllib
from twilio.rest import TwilioRestClient
from getArtistLinks import getArtistLink
import argparse
import json


def getCredentials(file_name):
    """
    This function grabs the credentials from a given json file.
    :param file_name: The path to the json file containing the credentials
    :type file_name: text file, i.e. .txt or .json
    :return: dictionary of credentials
    """
    with open(file_name, 'r') as f:
        credentials = f.read()
    return json.loads(credentials)


def sendText(credentials, text):
    """
    This function sends a text using Twilio
    :param credentials: The dictionary containing the Twilio credentials
    :type credentials: dict
    :param text: The text to be sent
    :type text: str
    :return: Nothing, text is sent
    """
    # the following line needs your Twilio Account SID and Auth Token
    client = TwilioRestClient(credentials['twilio_sid'], credentials['twilio_token'])

    # change the "from_" number to your Twilio number and the "to" number
    # to the phone number you signed up for Twilio with, or upgrade your
    # account to send SMS to any phone number
    client.messages.create(to=credentials['your_phone#'], from_=credentials['twilio_phone#'],
                           body=text)


def getSched():
    """
    This function gets the schedule from Hotel Utah
    :return sched: The "schedule" in raw HTML format
    """
    SITE = 'http://www.hotelutah.com/'
    r = urllib.urlopen(SITE).read()
    soup = BeautifulSoup(r)
    sched = [i for i in soup.find_all('div', class_="list-view-item")]
    return sched



def getArtists(sched_raw):
    """
    This function pulls out the dates and artists for the upcoming shows at Hotel Utah
    :param sched_raw: The raw schedule HTML as returned from getSched()
    :type sched_raw: List of BeautifulSoup
    :return dates: The list of dates for upcoming shows
    :type dates: List
    :return artists: The list of lists of artists for each night
    :type artists: List
    """
    schedule_list = []
    for i in sched_raw:
        event = i.find_all('h1')
        date= i.find_all('h2', class_='dates')[0].get_text()
        schedule_list.append( (date, [event[x].get_text() for x in range(len(event )) ] ))

    artists = [i[1] for i in schedule_list]
    dates = [i[0] for i in schedule_list]

    return dates, artists


def buildText(artists, dates, playlist_links):
    """
    This function builds the text to be sent containing the upcoming shows and Spotify links
    :param artists: The list of lists of artists as returned by getArtists()
    :type artists: List of lists
    :param dates: The list of lists of dates as returned by getArtists()
    :type artists: List of lists
    :param playlist_links: The list of links to the Spotify playlists for each night
    :type playlist_links: List
    :return: The text to be sent out
    """
    return '{}\n\n{}'.format('\n\n'.join(
        ["{}:\n{}".format(
            dates[i], '\n'.join(['{}\t{}'.format(j, getArtistLink(j)) for j in artists[i]]))
         for i in range(len(dates))]), playlist_link)

def main(args):
    creds = getCredentials(args.twil)
    sched_raw = getSched()
    dates, artists, artists_flat = getArtists(sched_raw)
    txt = buildText(artists, dates, 'THIS IS WHERE THE PLAYLIST GOES')
    sendText(creds, txt)
    print 'TEXT SENT'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-twil", help="Twilio Credentials Filepath")
    args = parser.parse_args()
    main(args)



