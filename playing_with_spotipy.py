# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 10:05:54 2016

@author: admin
"""

# %% playing with spotipy
from __future__ import print_function
import spotipy
import spotipy.util as util
#import spotipy.oauth2 as oauth2
import pandas
import datetime
#import time
import os
import re

# %%authorization variables

scope = 'user-top-read user-library-read playlist-read-private playlist-modify-private'



# %% spotipy native authorization

#uncomment these three lines to authorize a connectin for ad hoc analysis

#token = util.prompt_for_user_token('1254805075', scope=scope, client_id='156c61627ddb4f3d847564dcaf030082',
#                                   client_secret='b854a95cf488401ea29ad446a4647ddd', redirect_uri='http://xkcd.com')
#spot = spotipy.Spotify(auth=token)


# %%Authorization pt 1

# I've commented this out.  It works, Spyder was havving troouble with input() 
# functions within a script.  I've split it up into two cells
# that I can run separately by hardcoding the response URL in.


# sp_oauth = oauth2.SpotifyOAuth(client_id='156c61627ddb4f3d847564dcaf030082', client_secret='b854a95cf488401ea29ad446a4647ddd', redirect_uri='http://xkcd.com',scope=scope, cache_path=".cache-" + me)
# token_info = sp_oauth.get_cached_token()
#
# if not token_info:
#        print('''
#
#            User authentication requires interaction with your
#            web browser. Once you enter your credentials and
#            give authorization, you will be redirected to
#            a url.  Paste that url you were directed to to
#            complete the authorization.
#
#        ''')
#        auth_url = sp_oauth.get_authorize_url()
#        print(auth_url)
#        
#        print('''
#        
#            Once you've done that, enter the url lower in the
#            script as the value of "secure_redirect_url".
#            
#            ''')
# %%Authorization pt 2

# if not token_info:
#    secure_redirect_url='https://xkcd.com/?code=AQBvC3hN30LwD7Cvdme92Yd_lZrwboS5_MAJLMJ-VgGy9IZ4-OAyowTqoKu4aFjN_ncbsWehP6yTkcl4X2Ek4eg6nebsCq8Xzv2YeEPTrq6E36Yh3MwS9Q6wywaZz6nnhvB59QzD2DseiaE8rubisDSDJ0zPdjMlLwUVeUEaMKVxgT82qrb81wPR4CZWDmJmM0zTpv5EuyQ1QlAy75FjBwr1wya5WyjvkCrwDrtQSUsp6qyU8NQWXuo7p_9lyQ'
#    code = sp_oauth.parse_response_code(secure_redirect_url)
#    token_info = sp_oauth.get_access_token(code)
#    token=token_info['access_token']


# %% Let's make some classes

class SpotSong:
    """
    Note to self: artists is a list of artist objects.  It's missing
    some of the standard attributes I've put into the SpotArtist class,
    which kinda sucks. So, two options here:
    1)  When I init a SpotSong, I can lookup the full artist details
    2)  I can store only the artist name(s) and id(s) and add a method
        to get full artist objects if I need them.
        
    Separately, I need to do a couple lines to get the multiple artist
    problem to work throughout.  Not really urgently because it's not a
    problem for anything on the immediate roadmap.
    """

    def __init__(self, song_dict):
        self.album = song_dict['album']
        self.name = song_dict['name']
        self.uri = song_dict['uri']
        self.popularity = song_dict['popularity']
        self.is_explicit = song_dict['explicit']
        self.disc = song_dict['disc_number']
        self.artists = song_dict['artists']
        self.duration = song_dict['duration_ms']
        self.dtype = song_dict['type']
        self.id = song_dict['id']
        self.markets = song_dict['available_markets']

    def __repr__(self):
        return u'<SpotSong object for: "' + self.name + '">'


class SpotArtist:
    def __init__(self, artist_dict):
        self.id = artist_dict['id']
        self.name = artist_dict['name']
        self.uri = artist_dict['uri']
        self.popularity = artist_dict['popularity']
        self.followers = artist_dict['followers']['total']
        self.genres = artist_dict['genres']
        self.dtype = artist_dict['type']

    def __repr__(self):
        return u"<SpotArtist object for: " + self.name + u">"


class SpotPlaylist:
    def __init__(self, playlist_dict):
        self.id = playlist_dict['id']
        self.name = playlist_dict['name']
        self.description = playlist_dict['description']
        self.ispublic = playlist_dict['public']
        self.owner = playlist_dict['owner']
        self.tracks_dict = playlist_dict['tracks']
        self.dtype = playlist_dict['type']
        self.followers = playlist_dict['followers']
        self.uri = playlist_dict['uri']

        tracks = []
        for i in self.tracks_dict['items']:
            tracks.append(SpotSong(i['track']))
        self.tracks = tracks

    def __repr__(self):
        return u"<SpotPlaylist object for: " + self.name + u">"


# %% Lets make some get_thing() functions for our classes based on id


# %% Get all my playlists

def get_user_playlists(user):
    """
    Gets my playlists as a list of tuples (playlist name, playlist id, user_id)
    """
    
    c=0
    playlists = []
    
    while len(playlists) == c*50:
        x = spot.user_playlists(user, limit=50, offset=c*50)
        
        for playlist in x['items']:
            playlists.append((playlist['name'], playlist['id'], user))
        
        c+=1
        
    return playlists






def get_tracks(playlist, user=me):
    """Gets track list associated with a playlist.

    Returns songs as a list of dict-like structures.
    This structure can seamlessly be imported into pandas (though unicode typing
    in the source data can prevent export using pandas.to_clipboard())

    Args:
        playlist: an iterable of length 2 or more, in which the second item
        is a spotify playlist id.

    Returns:
        A list of dicts, each of which corresponds to one song on the playlist.
        Songs are structured as follows:
        
        {'artist':artist,         # Artist only returns the first artist on a song
        'artist_id':artist_id,    # Artist_id only returns the first artist on a song
        'title':title,
        'song_id':song_id,
        'popularity':popularity}
    """
    tracks = []
    c = 0
    while len(tracks) == c * 100:
        x = spot.user_playlist_tracks(playlist[2], playlist[1], offset=c * 100)
        for song in x['items']:
            artist = song['track']['artists'][0]['name']  # artist name
            artist_id = song['track']['artists'][0]['id']  # artist id
            title = song['track']['name']  # track name
            song_id = song['track']['id']  # track id
            popularity = song['track']['popularity']  # track popularity
            song_dict = {'artist': artist, 'artist_id': artist_id, 'title': title, 'song_id': song_id,
                         'popularity': popularity}
            tracks.append(song_dict)
        c += 1
    return tracks


def get_artist(artist_id):
    """
    Gets an artis rom the artist_id, returns an object of class SpotArtist
    """
    return SpotArtist(spot.artist(artist_id))


def get_rel_artists_edges(artist_id):
    rel_artists_dict = spot.artist_related_artists(artist_id)['artists']
    source_artist = artist_id
    artist_pairs = []
    for sink_artist in rel_artists_dict:
        artist_pairs.append((source_artist, SpotArtist(sink_artist).id))
    return artist_pairs


def get_solo_albums(artist_id):
    '''
    A function to get all of an artists albums (excluding compilaitons they're on)
    
    Arugments:
        artist_id - A Spotify artist id value (string)
    
    Returns:
        List of album_ids, excluding albums on which the requested artist is
        not listed as the album's primary artist (e.g. "Various artists")   
    '''

    alb_resp = spot.artist_albums(artist_id)  # get first 20 albums associated with the artist
    total = alb_resp[
        'total']  # total lists total number of albums the artist has, inclusive of EPs, compilations, and singles
    alb_objs = alb_resp['items']  # list of dicts/JSON objects, each representing one album.
    if total > 20:
        for i in range((total - 1) // 20):
            alb_resp = spot.artist_albums(artist_id, offset=20 * (i + 1))  # request albums...with an offset
            alb_objs += alb_resp['items']  # add incremental albums to list of album objects

    alb_ids = []

    for alb_obj in alb_objs:
        if artist_id in [artist['id'] for artist in alb_obj['artists']]:  #Builds list or artist_ids associated with the album and checks current against the list
            alb_ids.append(alb_obj['id'])
    return alb_ids


def get_all_albums(artist_id):
    '''
    A function to get all of an artists albums (including compilations they're on).
    
    Arugments:
        artist_id - A Spotify artist id value (string)
    
    Returns:
        List of album_ids, excluding albums on which the requested artist is
        not listed as the album's primary artist (e.g. "Various artists")   
    '''

    alb_resp = spot.artist_albums(artist_id)  # get first 20 albums associated with the artist

    # total lists total number of albums the artist has, inclusive of EPs, compilations, and singles
    total = alb_resp['total']

    alb_objs = alb_resp['items']  # list of dicts/JSON objects, each representing one album.
    if total > 20:
        for i in range((total - 1) // 20):
            alb_resp = spot.artist_albums(artist_id, offset=20 * (i + 1))  # request albums...with an offset
            alb_objs += alb_resp['items']  # add incremental albums to list of album objects

    alb_ids = []

    for alb_obj in alb_objs:
        alb_ids.append(alb_obj['id'])

    return alb_ids


def get_album_all_tracks(album_id):
    '''
    Gets all songs found on an album. 
    
    Arguments:
        album_id - A Spotify album id value (string)
        
    Returns:
        List of song_ids
    '''
    track_resp = spot.album_tracks(album_id)
    total = track_resp['total']
    track_objs = track_resp['items']
    if total > 50:
        for i in range((total - 1) // 50):
            track_resp = spot.album_tracks(album_id, offset=50 * (i + 1))
            track_objs += track_resp['items']

    track_ids = []
    for track_obj in track_objs:
        track_ids.append(track_obj['id'])
    return track_ids


def get_artist_all_tracks(artist_id):
    # need a function to import all tracks from an artist
    '''
    Gets all songs found on an arist's albums. The list of albums used here 
    includes singles, EP's, and any album in which the artist is listed by
    Spotify by name as one of the artists, but does not include compilations by
    "various artists" that the artist appears on (though these do appear
    on the artsits's artist page).
    
    Arguments:
        artist_id - A Spotify artist id value (string)
        
    Returns:
        List of artis_id:album_id:song_id pairings in tuple format
    '''

    albums = get_all_albums(artist_id)  # returns list of album ids
    tracklist = []  # tracklist is a holder for outgoing data
    for album_id in albums:
        track_ids = get_album_all_tracks(album_id)
        for track_id in track_ids:
            tracklist += [(artist_id, album_id, track_id)]
    artist_tracks = []

    for track in tracklist:
        if track[0] == artist_id:
            artist_tracks.append(track)

    return artist_tracks


def get_lots_artists(art_list):
    '''
    Gets artist details for a large number of artists and returns them as a
    list of dicts. Output can be input directly to pandas.DataFrame()
    
    Arguments:
        art_list - a list of Spotify artist id values
        
    Returns
        List of artist dictionaries
    '''
    loops = (len(art_list) - 1) // 50 + 1  # number of separate calls i'll need to get these 50 at a time
    artists = []
    for i in range(loops):
        art_resp = spot.artists(art_list[50 * i:50 * i + 50])  # kindly ask Spotify for next 50 artists
        artists += art_resp['artists']

    artist_frame = pandas.DataFrame(artists)
    artist_frame.drop(['external_urls', 'href', 'images', 'type'], axis=1, inplace=True)
    artist_frame.rename(columns={'followers': 'artist_followers', 'id': 'artist_id', 'name': 'artist_name',
                                 'popularity': 'artist_popularity', 'uri': 'artist_uri'}, inplace=True)
    return artist_frame


def get_lots_albums(alb_list):
    '''
    Gets album details for a large number of artists and returns them as a
    list of dicts. Output can be input directly to pandas.DataFrame()

    Arguments:
        alb_list - a list of Spotify artist id values

    Returns
        List of album dictionaries
    '''
    chunk = 20  # set chunk sizes
    loops = (len(alb_list) - 1) // chunk + 1  # number of separate calls i'll need to get these <chunk> at a time
    albums = []
    for i in range(loops):
        alb_resp = spot.albums(alb_list[chunk * i:chunk * i + chunk])  # kindly ask Spotify for next <chunk> artists
        alb_resp_clean = []
        for j in alb_resp['albums']:
            this_alb = j
            for k in ['tracks', 'href', 'images', 'external_ids', 'external_urls', 'available_markets', 'type']:
                try:
                    del this_alb[k]
                except:
                    pass
            alb_resp_clean.append(this_alb)
        albums += alb_resp['albums']

    # convert to dataframe
    alb_frame = pandas.DataFrame(albums)
    alb_frame.rename(
        columns={'id': 'album_id', 'name': 'album_name', 'popularity': 'album_popularity', 'uri': 'album_uri'},
        inplace=True)
    alb_frame['album_copyright'] = alb_frame['copyrights'].apply(lambda x: x[0]['text'])  # only returns first copyright
    alb_frame.drop(['genres', 'copyrights', 'artists'], axis=1, inplace=True)

    return alb_frame


def get_lots_tracks(track_list):
    '''
    Gets track details for a large number of artists and returns them as a
    list of dicts. Output can be input directly to pandas.DataFrame()

    Arguments:
        art_list - a list of Spotify artist id values

    Returns
        List of artist dictionaries
    '''
    loops = (len(track_list) - 1) // 50 + 1  # number of separate calls i'll need to get these 50 at a time
    tracks = []
    for i in range(loops):
        track_resp = spot.tracks(track_list[50 * i:50 * i + 50])  # kindly ask Spotify for next 50 artists
        tracks += track_resp['tracks']

    track_frame = pandas.DataFrame(tracks)
    track_frame['album_name_t'] = track_frame['album'].apply(lambda x: x['name'])
    track_frame['album_id_t'] = track_frame['album'].apply(lambda x: x['id'])
    track_frame['album_uri_t'] = track_frame['album'].apply(lambda x: x['uri'])
    track_frame['us_avail'] = track_frame['available_markets'].apply(lambda x: "US" in x)
    track_frame['track_artist_ids'] = track_frame['artists'].apply(lambda x: [artist['id'] for artist in x])
    track_frame['track_artist_names'] = track_frame['artists'].apply(lambda x: [artist['name'] for artist in x])
    track_frame.rename(
        columns={'uri': 'track_uri', 'id': 'track_id', 'name': 'track_name', 'popularity': 'track_popularity'},
        inplace=True)
    track_frame.drop(['album', 'artists', 'available_markets', 'external_ids', 'external_urls', 'href', 'type'], axis=1,
                     inplace=True)
    return track_frame


def build_library(artist_list):
    '''
    Builds library of all tracks the spine dataset based on a list of artists.

    Arguments:
        artist_list -  a list of Spotify artist ID's

    Returns:
        pairings
    '''
    ## Get list of artist_id:album_id:song_id pairings in tuple format
    spine = []
    for i in artist_list:
        spine += get_artist_all_tracks(i)

    ## make lists of the albums and tracks to look up details
    useless, album_list, track_list = zip(*spine)

    del useless  # garbage collector would have taken this anyways, but fuck this data in particular

    # dedupe album_list and track list
    album_list = list(set(album_list))
    track_list = list(set(track_list))

    ## Get artist details
    art_details = get_lots_artists(artist_list)

    ## Get album details
    alb_details = get_lots_albums(album_list)

    ## Get track details
    track_details = get_lots_tracks(track_list)

    spine = pandas.DataFrame(spine, columns=['artist_id', 'album_id', 'track_id'])

    ##begin merges
    spine1 = pandas.merge(left=spine, right=art_details, left_on='artist_id',
                          right_on='artist_id', how='left', suffixes=
                          ['', '_todel'])

    spine2 = pandas.merge(left=spine1, right=alb_details, left_on='album_id',
                          right_on='album_id', how='left', suffixes=
                          ['', '_todel'])

    spine3 = pandas.merge(left=spine2, right=track_details, left_on='track_id',
                          right_on='track_id', how='left', suffixes=
                          ['', '_todel'])

    ##drop create list of all columns ending in '_todel' and delete them
    del_fields = [col for col in list(spine3.columns) if col[-6:] == '_todel']
    spine3.drop(del_fields, axis=1)

    '''
    Still need to:     
    get artist details - done
    get album details - done
    get track details - done
    join data together - done
    filter out dupe columns (they end in "_todel")-done
    build some file IO to save the active search as it goes in case of fault
    '''

    return spine3


def get_artist_collaborators(artist_id):
    # would be interesting to see a network of artists who've worked together
    return NotImplemented


def get_top_tracks():
    return NotImplemented


# %%

'''What do I want to build here?

buil

* network explorer for new songs
    - Get list of tracks
    - Get artists associated with tracks
    - Get get related artists
    - Explore graph efficiently and fairly
        ~only pull rel artists once per artist. (weight by cycle?)
        ~pull more central artists first.
        ~maybe just operate two lists:
            1) list of artists to check
            2) set of checked artists
            3) iterate through artists, check starting list
            4) order by centrality on subsequent loops? naw, not worth it.
    - Once I have artists, build set of tracks to identify songs I want to hear.
        ~get list of albums
        ~get list of tracks by album
        ~end dataset of artist-album-track to join in details (popularity, etc.)
            

Masterplan:
1)  Run main_run() to get related artist network structure- Done
2)  Run get_artist_all_tracks() to identify all tracks by all artists-Done
3)  Run get_lots_arists(), get_lots_albums(), get_lots_tracks() to get datasets
    on the various tracks (use date conversion trick from consolidating file)
4)  Run network feature analyses on the id-level networks (To Be Built)
5)  Run promising track analyses on artists tracks (To Be Built)
    ~ Most popular tracks by album
6)  Merge
        



'''


## First, get a playlist to start from
def main_run(playlist, search_depth=3):
    """
    Explores network of related artists, starting with a playlist.
    
    Arguments:
    playlist - this takes a playlist of the form, (playlist_name,playlist_id,owner_id)
    search_depth - depth of connections to search
    
    Returns:
    
    """

    to_check = []  # list of artists to check for related artists
    next_layer = []  # Destination for related artists, who become candidates to seed the 2nd wave
    artists = set()  # Set of artist id's generated in
    net_edges = set()  # set of edges for network creation
    my_art_list = pandas.DataFrame(get_tracks(playlist))['artist_id']  # generating a simple list artists
    for i in my_art_list:  # Initial setup of list to scrape
        to_check.append(i)
    to_check = list(set(to_check))  # de-dupe starting list
    artists = set(my_art_list)  # add starting list to set of artists
    for layer in range(search_depth):
        while len(to_check) > 0:
            rel_arts = get_rel_artists_edges(to_check.pop())  #
            net_edges = net_edges | set(rel_arts)  # add edges to network record
            if len(rel_arts) > 0:
                for band in list(zip(*rel_arts))[1]:
                    if band not in artists:
                        next_layer.append(band)
                artists = artists | set(list(zip(*rel_arts))[1])
        to_check = next_layer
        next_layer = []

    print("All done.  Total of " + str(len(artists)) + " artists in network.")
    return net_edges


# %%

def misc_snippets():
    """miscellaneous snippet examples of how to use spotipy. can ignore.
    """
    
    # play space
    teb = spot.search('artist:third eye blind', type='artist')
    
    teb_items = teb['artists']['items'][0]
    teb_id = teb['artists']['items'][0]['id']
    
    # Snippets to inspect top_tracks
    teb_tt = spot.artist_top_tracks(teb_id)  # returns dict with key "tracks"
    teb_tt = teb_tt[
        'tracks']  # returns list of dict objects for top 10 most popular songs.  This is ready for pandas.DataFrame()
    
    ## What I learned: top tracks are ranked by popularity 
    
    teb_albs = spot.artist_albums(teb_id)
    teb_albs = teb_albs['items']
    
    ##Look at the artist's albums
    teb_solo_albs = get_solo_albums(teb_id)
    
    # get all artist info
    teb_spine = get_artist_all_tracks(teb_id)
    
    ## get input lists to test 
    tebarts, tebalbs, tebtracks = zip(*teb_spine)
    tebarts = list(set(tebarts))
    tebalbs = list(set(tebalbs))
    tebtracks = list(set(tebtracks))
    
    xbo = pandas.DataFrame(get_lots_artists(tebarts))
    xto = pandas.DataFrame(get_lots_tracks(tebtracks))
    xao = pandas.DataFrame(get_lots_albums(tebalbs))
    
    xbo1 = get_lots_artists(tebarts)
    xto1 = get_lots_tracks(tebtracks)
    xao1 = get_lots_albums(tebalbs)
    
    my_edges = main_run(ds_spreaky_17, search_depth=1)
    
    return None

# %% Quick run to get artist names from playlist network

def artist_scout(playlist, search_depth=3):
    """
    Explores network of related artists, starting with a playlist.
    
    Arguments:
    playlist - this takes a playlist of the form, (playlist_name,playlist_id)
    search_depth - depth of connections to search
    
    Returns:
    arist_df - df of artists by centrality
    
    """

    edge_list = list(main_run(playlist=playlist, search_depth=search_depth))

    return scout_edges(edge_list)


def scout_edges(artist_graph):
    """
    
    Arguments: 
    artist_graph - list of edges on the artist graph of form (source,sink)
    
    Returns:
    scouting_report - DF of reported nework with columns:
        - artist name
        - connectedness
        - popularity
        - followers
        - flag for "song was in original playlist"
        - would be nice to get degree on this, but that may require surgery
    """
    ##TODO: do this-- want a function that I can use to get the artist name

    ## get list of "sink" artists
    art_list = pandas.DataFrame(artist_graph, columns=['source', 'sink'])
    art_list_unique = art_list['sink'].unique()

    ## Get artist details
    art_details = get_lots_artists(art_list_unique)

    ## count artist occurences in network
    art_count = art_list['sink'].value_counts().reset_index()
    art_count.columns = ['artist_id', 'edges']

    ## 
    art_sum = pandas.merge(left=art_count, right=art_details, left_on='artist_id',
                           right_on='artist_id', how='left', suffixes=
                           ['', '_todel'])

    return art_sum


# %% Assembling playlist

def get_curr_user_playlists():
    """returns list of playlist names and ids in tuples
    """
    # get dict of 
    mpl = spot.current_user_playlists()
    mpl_df = pandas.DataFrame(mpl['items'])
    mpl_df['owner_id'] = mpl_df['owner'].apply(lambda x: x['id'])
    return mpl_df[['name', 'id', 'owner_id']].values.tolist()


# getting artist top tracks
def get_artist_top_tracks(artist_id, country='US'):
    """
    Returns information on top tracks for the artist in list-of-lists format
    
    
    """

    out_tracks = []
    tracks_dict = spot.artist_top_tracks(artist_id)

    for track in tracks_dict['tracks']:
        track_title = track['name']
        track_album = track['album']['name']
        track_id = track['id']
        track_pop = track['popularity']
        out_tracks.append([artist_id, track_id, track_title, track_album, track_pop])
    return out_tracks


##assembling playlist

def playlist_from_arts(art_list, playlist_name=None):
    """
    Creates playlist out of top tracks from a list of artist_ids
    """
    if playlist_name == None:
        now = datetime.date.today()
        playlist_name = "Artist Network playlist " + now.strftime('%Y-%m-%d')

    tracks_list = []
    broken_arts = []

    ##Get top tracks
    for artist in art_list:
        try:
            att = get_artist_top_tracks(artist)
            tracks_list.extend(att)
        except spotipy.SpotifyException:
            broken_arts.append(artist)

    ##try again if any didn't work...not sure this code will ever get hit
    if len(broken_arts) > 0:
        print('have ' + str(len(broken_arts)) + ' broken artists...trying again')
        rejected_artists = []
        for artist in broken_arts:
            try:
                att = get_artist_top_tracks(artist)
                tracks_list.extend(att)
            except spotipy.SpotifyException:
                rejected_artists.append(artist)

    ##Convert list of tracks into dataframe

    att_df = pandas.DataFrame(tracks_list,
                              columns=['artist_id', 'track_id', 'track_title',
                                       'album', 'popularity'])

    # select tracks from top tracks to add to playlist

    play_track_list = playlister_pick_top_song(att_df)

    # create a playlist
    spot.user_playlist_create(me, playlist_name, public=False)

    ## figure out the playlist id I need
    my_playlists = spot.user_playlists(me)

    ##pythonic for "make a dictionary of playlist_names to ids"
    my_playlist_dict = {pl['name']: pl['id'] for pl in my_playlists['items']}

    playlist_id = my_playlist_dict[playlist_name]

    ##add tracks to playlist in chunks of 100

    loops = (len(play_track_list) - 1) // 100 + 1  # number of separate calls i'll need to get these 100 at a time

    for i in range(loops):
        chunk = play_track_list[100 * i:100 * i + 100]
        spot.user_playlist_add_tracks(me, playlist_id, chunk)

    pass


## selecting which song to use

def playlister_pick_top_song(att_df):
    """
    Given a list of top tracks by a number of artists, returns a pandas Series
    object containing the most popular. (Includes minimum popularity)
    """
    top_song_indices = att_df.groupby('artist_id')['popularity'].idxmax()
    playlist = att_df.iloc[top_song_indices]
    playlist = playlist[playlist['popularity'] >= 25]
    return list(playlist['track_id'])


##TODO: build a better playlister
"""
- exclude songs already saved by user
- look for 2nd/ non-top songs if top song is saved and 2nd is still pretty good
-       
"""


def playlister_plus(att_df):
    """Given list of top tracks by a number of artists...
    """
    return NotImplemented

    # %% Making it user-friendly for others to use


'''
- prompt for parameters: User ID
- display options of playlists
- write artist file
- assemble and publish playlist
'''

# %%
#fresh_arts = pandas.Series(zip(*my_edges)[1])
#fresh_arts = pandas.DataFrame(fresh_arts)
#fresh_arts.columns = ['artist_id']
#fresh_arts.drop_duplicates(inplace=True)
#rel_lib = build_library(list(fresh_arts['artist_id']))
#
## %%
#rel_lib = build_library(list(art_count.artist_id))
#
## %%This sequence makes a playlist
#t_a_p = ['test_auto_playlist', '0FSDHJVqbcSDI6AiQ1lLIK', '1254805075']
#spreaky_18 = ['DS Spreaky Songs 18', '7F1wMMFxvjZud2cnXwTqci', '1254805075']
#
#poppy = artist_scout(mytop18, search_depth=2)
#arts_to_list = list(poppy[poppy['edges'] > 1]['artist_id'])
#playlist_from_arts(arts_to_list, playlist_name='auto_top18')


                   
# %%Set up block for direct run


if __name__ == "__main__":
    # define scope required to work    
    scope = 'user-top-read user-library-read playlist-read-private playlist-modify-private'
    
    print("Hey there. Let's make a playlist!")
    
    # prompt user for their info and login
    username = input("\n\nWhat's your username?\n\nenter username: ")
    
    # get OAuth
    while "user_token" not in locals():
        user_token = util.prompt_for_user_token(username, scope=scope, client_id='156c61627ddb4f3d847564dcaf030082',
                                       client_secret='b854a95cf488401ea29ad446a4647ddd', redirect_uri='http://xkcd.com')
    
    spot = spotipy.Spotify(auth=user_token)
    
    # get starting playlist
    # first, give option of own playlist or someone else's
    print("It takes playlists to make playlists.")
    
    print("Do you want to make a playlist based on one of your own or someone else's?")
    playlist_source = ''
    
    playlist_source = input("Enter 1 to use your own playlist or 2 to use someone else's public playlist):  ")
    
    while playlist_source not in ('1','2','exit'):
        input("\Oops... you gave a wrong entry.\nEnter 1 to use your own playlist or 2 to use someone else's public playlist):  ")
        
        if playlist_source == 'exit':
            break

    # get list of playlist options for specified user
    if playlist_source == '1':
        playlists = get_user_playlists(spot.current_user()['id']) # get playlists for current user
    elif playlist_source == '2':
        awaiting_valid_user = True      # check to ensure user is valid
        while awaiting_valid_user:
            playlist_user = input("\n\nWhat's the username of the user who's playlist you want to use?\n\nenter username:  ")
            try:
                spot.user(playlist_user)
                awaiting_valid_user=False
            except spotipy.SpotifyException:
                print("\nHmmm... that's not a user. Try again?")
        playlists = get_user_playlists(playlist_user) # check to ensure user is valid
    else:
        print("Something went wrong. We'll use one of your playlists.")
        playlists = get_user_playlists(spot.current_user()['id'])
    
    # check I got some playlists, but not toooooo many
    assert playlists, "\nWhat the heck?!  I don't see any playlists."
    assert len(playlists)<200, "\nToo many playlists! May not display properly."

    # display list of playlist names
    print('\nCool.  Here are some playlist options... pick the number of the playlist you want:')
    # enumerate playlist options
    for i, playlist_name in enumerate(list(zip(*playlists))[0]):
        print(str(i) + '.  ' + playlist_name)
    
    # check to ensure valid playlist input
    awaiting_valid_playlist = True
    while awaiting_valid_playlist:
        playlist_selection = input('\n Enter playlist number here: ')
        
        try:
            pl_index = int(playlist_selection)
            ref_playlist = playlists[pl_index]
            awaiting_valid_playlist = False
        except ValueError:
            print('oops... you need to enter just a number. try again?')
        except IndexError:
            print("we don't seem to have that many playlists... try again?")

    # offer artist list or automated playlists
    print('\nMore options: do you want a list of interesting artists? Or make a full playlist?')
    awaiting_valid_art_list_selection = True
    while awaiting_valid_art_list_selection:
        arts_or_list = input('Enter 1 for artists, or 2 for full playlists: ')    
        if arts_or_list in ('1','2'):
            awaiting_valid_art_list_selection = False
        else:
            print("oops... enter 1 or 2, please.")

    # give chance to back out
    ready_to_go = input('\nYou picked "'+ref_playlist[0]+'".\nIs that right? (y/n):  ')
    assert ready_to_go.lower() == 'y', "okay, let's quit, then"
    
    # set auto_playlist name
    auto_playlist_name = input('\nWhat will you call this new file/playlist?: ')[:50]
    
    # scout artist network
    print('\nGreat!  Starting now. This may take a few minutes...')
    poppy = artist_scout(ref_playlist, search_depth=2)

    # either write the artists to csv or make a playlist
    if arts_or_list == '1':
        # remove special characters from filename
        clean_filename = re.sub('[^A-Za-z0-9_]+', '', auto_playlist_name.replace(' ','_'))
        
        #make path to save artists to
        art_path = os.path.join('.' , clean_filename + '.csv' )
        
        # write artist list down, sorted by connectedness
        poppy.sort_values('edges', ascending=False).to_csv(art_path)
    
    elif arts_or_list == '2':
        print('\nQuick update: Found some artists you should try...\n Still need to look up their songs...')
        
        # write playlists to spotify
        arts_to_list = list(poppy[poppy['edges'] > 9]['artist_id'])        
        playlist_from_arts(arts_to_list, playlist_name=auto_playlist_name)
        print("Great. That's all. Go check Spotify.")


    else:
        print('oh, goodness... something went wrong.')
    