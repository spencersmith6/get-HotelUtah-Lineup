from getHotelUtah import getSched, getArtists
import spotipy
import spotipy.util as util
import re

def get_artistID(artist, results):
    artist_uri = None
    for i in results['artists']['items']:
        print i['name']
        if i['name'].lower() == artist:
            artist_uri = i['uri']
    return artist_uri


def create_playlist(username):
    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(username, scope)
    sp = spotipy.Spotify(auth = token)
    sp.trace=False

    playlist_results = sp.user_playlist_create(username, 'Hotel Utah Tonight')

    sched_raw = getSched()
    dates, artists = getArtists(sched_raw)

    songs_to_add = []
    for artist in artists[0]:
        artist = re.sub('\(closing set\)', '', artist.lower())
        results = sp.search(q='artist:' + artist, type='artist')
        artist_uri = get_artistID(artist, results)
        if artist_uri != None:
            response = sp.artist_top_tracks(artist_uri)
            [songs_to_add.append(track['uri'].split(':')[2]) for track in response['tracks'][:5]]

    sp.user_playlist_add_tracks(username, playlist_results['uri'].split(':')[-1], songs_to_add)
    return playlist_results['external_urls'].values()[0]

username = 'spencersmith6'

print create_playlist('spencersmith6').keys()


# recomendations = sp.recommendations(seed_artists = [artist_uri])
# for track in recomendations['tracks']:
#     print track['name'], '-', track['artists'][0]['name']