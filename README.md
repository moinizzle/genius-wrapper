# About
I wrote a custom wrapper for Genius API to fetch lyrics. I used it in my [Siihan](https://github.com/moinizzle/siihan) project.
# Instructions
Create an API client [here](https://genius.com/developers) and generate access token

Import module
```python3
from wrapper import Genius
```
Authenticate API and start a session
```python3
api = Genius(GENIUS_TOKEN)
```
Perform a search on chosen artist
```python3
artist, artist_id = api.search('Drake')
```
Extract top 100 songs (based on popularity)
```python3
all_songs, all_songs_data = api.get_all_songs(artist, artist_id, return_data=True)
```
Choose a song and save it's lyrics
```python3
song = random.choice(all_songs_data)
lyrics = api.get_song_lyrics(target)
```
# Credits
[Genius](https://genius.com/developers)
# License
[MIT](License)
