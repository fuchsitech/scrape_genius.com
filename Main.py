import Secret
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd


# Get all Songs for the individual Artist ID's
def get_artist_songs(artist):
    # Search via API to create a List of all Songs
    def search(query):
        search_url = 'search?per_page=50'
        data = {'q': query}
        return api_request(path=search_url, params=data)

# General function for accessing the Genius.com API using requests
    def api_request(path, params=None):
        url = "https://api.genius.com/" + path
        headers = {"Authorization": "Bearer {}".format(
            Secret.genius_client_access_token)}
        response = requests.get(url=url, params=params, headers=headers)

        return response.json()

# Search for the Artist by Name and check any of the results for a match
    def find_artist_id_by_name(artist):
        response = search(query=artist)
        for hit in response["response"]["hits"]:
            if hit["result"]["primary_artist"]["name"] == artist:
                artist_id = hit["result"]["primary_artist"]["id"]
                return artist_id

    artist_id = find_artist_id_by_name(artist)
    current_page = 1
    songs_left = True
    songs = []

    # Iterating Songs by Artist, this could take a while depening on the artist
    while songs_left:
        # Access API with current Paramenters
        path = "artists/{}/songs/".format(artist_id)
        params = {'page': current_page}
        data = api_request(path, params)
        page_songs = data['response']['songs']

        # If we found Data, append and keep iterating
        if page_songs:
            songs.append(page_songs)
            current_page += 1
            print("Accessed Page {}, waiting 5 Seconds".format(current_page))
            time.sleep(5)
        else:
            # if no songs found, quit
            songs_left = False

    return songs


# Checks all Songs existing in song_data and retrieves the word within
def get_lyrics(song_data, df):
    for index, song in enumerate(song_data):

        url = "https://genius.com" + song['path']
        lyrics = []
        counter = 0
        # In some cases the Request Does not return the correct Divs.
        # Im not quite sure why, but since I dont plan on using this script
        # to access a ton of Data, I will just wait and try again.
        while counter < 10:
            try:
                counter += 1

                page = requests.get(url)
                html = BeautifulSoup(page.text, 'html.parser')
                lyrics = html.find('div', class_='lyrics').get_text()
                # Strip the Lyrics of all (for my usecase) useless elements
                lyrics = lyrics.replace("'", "").replace(",", "").replace(".", "").lower()

                lyrics = lyrics.split()
            except:
                time.sleep(5)

        part = ""
        for word in lyrics:
            # The Lyrics are divided into different Parts. These are marked with []
            # I check for those, and add the Source Part of each Word into the Dataframe
            if word[0] == "[":
                part = word[1:]
                if part[-1:] == "]":
                    part = part[:-1]
                    # Since we dont want the "part" thing to be a word, we continue
                    continue
            if word[:0] == "]":
                continue
            else:
                title = song['title']
                artist = song['primary_artist']['name']
                df = df.append(fill_df(title, artist, part, word), ignore_index=True)
        print("Track {}/{}. Waiting 5 Seconds".format(index+1, len(song_data)))
        time.sleep(5)
    return df


# Create the df element
def fill_df(title, artist, part, word):
    df_temp = {
        'Title': title,
        'Artist': artist,
        'Part': part,
        'Word': word
    }
    return df_temp


# Iterate the list of Artists and merge the Data in 1 Dataframe
def main():
    # Predefine Dataframe
    df = pd.DataFrame(columns=('Title', 'Artist', 'Part', 'Word'))

    for artist in artists:
        # Create List of all Songs we can find on Genius
        song_data = get_artist_songs(artist)
        # Add Data to our existing Dataframe
        df = df.append(get_lyrics(song_data, df), ignore_index=True)

        # Save df to
    df.to_json(r'basedata.json')


if __name__ == "__main__":
    """ This is executed when run from the command line """
    artists = ["Artist1", "Artist2"]
    main()