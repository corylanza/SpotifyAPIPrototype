import base64, requests, urllib.parse, sys, configparser, re

def auth():
    encoded = base64.b64encode((ClientId+':'+ClientSecret).encode('ascii'))
    url = 'https://accounts.spotify.com/api/token'
    headers = {'Authorization': 'Basic %s' % encoded.decode('ascii')}
    r = requests.post(url, data={'grant_type': 'client_credentials'}, headers=headers)
    return r.json()['access_token']

def play_song(song, artist, access_token):
    url = 'https://api.spotify.com/v1/search?'
    if artist != '':
        query = f'track:{song} artist:{artist}'
    else:
        query = f'track:{song}'
    params = urllib.parse.urlencode({'type': 'track', 'market': 'US', 'limit': 1, 'q': query})
    r = requests.get(url+params, headers={'Authorization': 'Bearer {0}'.format(access_token)})
    track = r.json()['tracks']['items'][0]
    print('Now playing', track['name'], 'by', track['artists'][0]['name'])

def play_album(album_id, access_token):
    url = f'https://api.spotify.com/v1/albums/{album_id}/tracks'
    r = requests.get(url, headers={'Authorization': 'Bearer {0}'.format(access_token)})
    first_song = r.json()['items'][0]['name']
    print('Now playing', first_song)

def search_album(album, artist, access_token):
    url = 'https://api.spotify.com/v1/search?'
    if artist != '':
        query = f'album:{album} artist:{artist}'
    else:
        query = f'album:{album}'
    params = urllib.parse.urlencode({'type': 'album', 'market': 'US', 'limit': 1, 'q': query})
    r = requests.get(url+params, headers={'Authorization': 'Bearer {0}'.format(access_token)})
    result = r.json()['albums']['items'][0]
    album_id = result['id']
    print(result['name'], '-', result['artists'][0]['name'])
    play_album(album_id, access_token)

def play_artist(artist_id, access_token):
    url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks'
    params = urllib.parse.urlencode({'country': 'US'})
    r = requests.get(url, params=params, headers={'Authorization': 'Bearer {0}'.format(access_token)})
    for track in r.json()['tracks']:
        print(track['name'])
    first_song = r.json()['tracks'][0]['name']
    print('Now playing', first_song)

def search_artist(artist, access_token):
    url = 'https://api.spotify.com/v1/search?'
    query = f'artist:{artist}'
    params = urllib.parse.urlencode({'type': 'artist', 'market': 'US', 'limit': 1, 'q': query})
    r = requests.get(url+params, headers={'Authorization': 'Bearer {0}'.format(access_token)})
    result = r.json()['artists']['items'][0]
    print(result['name'])
    play_artist(result['id'], access_token)

def user(access_token):
    url = 'https://api.spotify.com/v1/me'
    r = requests.get(url, headers={'Authorization': 'Bearer {0}'.format(access_token)})

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    global ClientId, ClientSecret
    ClientId = config['API keys']['client id']
    ClientSecret = config['API keys']['client secret']

    while True:
        print("enter a command")
        command = input()
        if command == 'exit':
            break
        access_token = auth()
        match = re.match(r'(?:play\s(track|album)\s(.+?(?= by artist|$))(?: by artist (.{1,}))?)', command)
        if match:
            search_type = match.group(1)
            title = match.group(2)
            artist = match.group(3)
            if search_type == 'track':
                play_song(title, artist, access_token)
            elif search_type == 'album':
                search_album(title, artist, access_token)
        else:
            print('invalid command')
    