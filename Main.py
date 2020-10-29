import pandas as pd
import Genius

# Iterate the list of Artists and merge the Data in 1 Dataframe
def main():
    # Predefine Dataframe
    df = pd.DataFrame(columns=('Title', 'Artist', 'Part', 'Word'))

    for artist in artists:
        # Create List of all Songs we can find on Genius
        song_data = Genius.get_artist_songs(artist)
        # Add Data to our existing Dataframe
        df = df.append(Genius.get_lyrics(song_data, df), ignore_index=True)

        # Save df to
    df.to_json(r'basedata.json')


if __name__ == "__main__":
    """ This is executed when run from the command line """
    artists = ["Artist1", "Artist2"]
    main()