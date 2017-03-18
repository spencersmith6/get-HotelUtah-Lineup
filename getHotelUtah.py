"""
This script builds Spotify playlists for the upcomign shows at Hotel Utah (http://www.hotelutah.com/)
Playlist URIs can be passed as arguments, one for daily and one for weekly playlists, which will cause the playlists
    to be overwritten with the most up to date artists
The script will also send a text via Twilio containing the upcoming lineups as well as links to the
    daily/weekly playlists
"""

from bs4 import BeautifulSoup
import urllib
from twilio.rest import TwilioRestClient
import argparse
import json
import spotipy
import spotipy.util as util
import re

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
    print 'TEXT SENT'


def getArtistLink(artist):
    """
    Given an artist name, return the open.spotify link to their Spotify artist page
    :param artist: The artist name, i.e. "Anderson .Paak"
    :type artist: str
    :return: The open.spotify url
    """
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    sp.trace = False
    results = sp.search(q='artist:{}'.format(artist), type='artist')
    try:
        all_artists = results['artists']['items']
        for artist_data in all_artists:
            if artist_data['name'] == artist:
                return artist_data['external_urls'].values()[0]
        return 'No Results Found on Spotify'
    except IndexError:
        return 'No Results Found on Spotify'


def getSched():
    """
    This function gets the schedule from Hotel Utah Website
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
        schedule_list.append((date, [event[x].get_text() for x in range(len(event )) ] ))

    artists = [i[1] for i in schedule_list]
    dates = [i[0] for i in schedule_list]

    return dates, artists


def get_artistID(artist_0, sp):
    '''
    :param artist:
    :param results:
    :return: Searches the results (search results) for a perfect text match of the artist.
    Returns the artist uri if match is found.
    Otherwise returns None
    '''

    artist_1 = re.sub(r'\([^)]*\)', '', artist_0)
    artist_2 = re.sub('band', '', artist_1.lower()).strip(" ")

    results_0 = sp.search(q='artist:' + artist_0, type='artist')
    results_1 = sp.search(q='artist:' + artist_1, type='artist')
    results_2 = sp.search(q='artist:' + artist_2, type='artist')


    for results, artist in [(results_0, artist_0), (results_1, artist_1), (results_2, artist_2)]:
        for i in results['artists']['items']:
            if i['name'].lower() == artist.lower():
                artist_uri = i['uri']
                return artist_uri

    return None


def create_playlist(username, artists, playlist_uri = None, type="daily"):
    """
    Creates a playlist in the account of the given user name.
    Adds the top 5 songs of the artists playing in Hotel Utahs upcoming show.
    :param username: The username URI
    :type username: str
    :param playlist_uri: The Spotify playist URI, if there is one to be reaplced
    :return: Links to the daily and weekly playlists.
    """

    if type not in ['daily', 'weekly']:
        print "The parameter 'type' must be either 'daily' or 'weekly'"
        return None
    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(username, scope)
    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    if type == 'daily':
        songs_to_add = build_song_list(artists[0], sp)
        print artists[0]
    else:
        songs_to_add = build_song_list([item for sublist in artists for item in sublist], sp)

    if len(songs_to_add) == 0:
        print "empty playlist"
        return None

    if playlist_uri is None:
        if type == 'daily':
            playlist_results = sp.user_playlist_create(username, 'Hotel Utah Tonight')
            playlist_link = playlist_results['external_urls'].values()[0]
        else:
            playlist_results = sp.user_playlist_create(username, 'Hotel Utah This Week')
            playlist_link = playlist_results['external_urls'].values()[0]

        sp.user_playlist_add_tracks(username, playlist_results['uri'].split(':')[-1], songs_to_add)

    else:
        playlist_results = sp.user_playlist_replace_tracks(username, playlist_uri, songs_to_add)
        playlist_link = 'http://open.spotify.com/user/spencersmith6/playlist/' + playlist_uri

    return playlist_link


def build_song_list(artists, sp):
    """
    THis function builds the list of top 5 songs from a given list of artists
    :param artists: List of artists
    :type artists: List
    :param sp: Spotify Session
    :type sp: Spotipy.Spotify()
    :return songs_to_add: List of Spotify URIs
    """
    songs_to_add = []
    for artist in artists:
        artist_uri = get_artistID(artist, sp)
        print artist_uri
        if artist_uri != None:
            response = sp.artist_top_tracks(artist_uri)
            [songs_to_add.append(track['uri'].split(':')[2]) for track in response['tracks'][:5]]
        else: print "No Artists Found."
    return songs_to_add


def buildText(artists, dates, daily_playlist_link, weekly_playlist_link= None):
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
    return "{}\n\nTonight's Playlist: \n{}".format(
        '\n\n'.join(["{}:\n{}".format(dates[i], '\n'.join([j for j in artists[i]]))for i in range(len(dates))]),
        daily_playlist_link) \
        #   + "\n Weekly Playlist: {}".format(weekly_playlist_link)




def main(args):
    USERNAME = args.user_name
    DAILY_PLAYLIST = args.daily_playlist_uri
    WEEKLY_PLAYLIST = args.weekly_playlist_uri
    DAILY_PLAYLIST = '5NN7PVBtBxVpyveuLQs1yH'

    creds = getCredentials(args.twil)
    sched_raw = getSched()
    dates, artists = getArtists(sched_raw)

    daily_playlist_link = create_playlist(USERNAME, artists, playlist_uri=DAILY_PLAYLIST, type='daily')
    #weekly_playlist_link = create_playlist(USERNAME, artists, playlist_uri=WEEKLY_PLAYLIST, type='weekly')
    txt = buildText(artists, dates, daily_playlist_link)
    sendText(creds, txt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-twil", help="Twilio Credentials Filepath")
    parser.add_argument("-user_name", help="Spotify Username/ID")
    parser.add_argument('--daily_playlist_uri',
                        help="The Spotify playlist URI. If provided, the songs here will be overwritten with tonights artists")
    parser.add_argument('--weekly_playlist_uri',
                        help="The Spotify playlist URI. If provided, the songs here will be overwritten with this weeks artists")
    args = parser.parse_args()
    main(args)
