import getHotelUtah as ghu
import pprint
import sys
import makePlaylist as mp
import spotipy
import spotipy.util as util

from spotipy.oauth2 import SpotifyClientCredentials

def get_artistID(artist, results):
    artist_uri = None
    for i in results['artists']['items']:
        if i['name'].lower() == artist:
            artist_uri = i['uri']
    return artist_uri

scope = 'playlist-modify-public'
username = 'spencersmith6'

token = util.prompt_for_user_token(username, scope)
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth = token)
sp.trace=False

playlist_id = mp.makePlaylist('new_music3', username)['uri'].split(':')[-1]

###
sched_raw = ghu.getSched()
dates, artists = ghu.getArtists(sched_raw)

songs_to_add = []
for artist in artists[0]:
    artist = artist.lower()

    ####
    results = sp.search(q='artist:' + artist, type='artist')
    artist_uri = get_artistID(artist, results)
    if artist_uri != None:
        response = sp.artist_top_tracks(artist_uri)
        [songs_to_add.append(track['uri'].split(':')[2]) for track in response['tracks'][:5]]

results = sp.user_playlist_add_tracks(username, playlist_id, songs_to_add)





# recomendations = sp.recommendations(seed_artists = [artist_uri])
# for track in recomendations['tracks']:
#     print track['name'], '-', track['artists'][0]['name']