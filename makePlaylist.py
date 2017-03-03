import pprint
import sys
import spotipy
import spotipy.util as util

def makePlaylist(playlist_name, username):
    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(username, scope)
    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        playlists = sp.user_playlist_create(username, playlist_name)
        pprint.pprint(playlists)
        return playlists

    else:
        print("Can't get token for", username)
