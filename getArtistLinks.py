import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


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
    return results['artists']['items'][0]['external_urls'].values()[0]
