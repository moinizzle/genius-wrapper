#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import json
import requests
import time
from bs4 import BeautifulSoup as bs


API_URL = 'https://api.genius.com/'
WEB_URL = "https://genius.com/api/"

SKIP = {
    'tracklist', 'album art', 'deutsche', 'nederlandse',
     'latino', 'française', 'español'}

class Genius():
    ''' Custom wrapper for genius API
    
    Attributes:
        wait: seconds to wait for response before giving up (int)
        api_url: url of api (str)
        web_url: url of web api (str)
    '''

    def __init__(self, GENIUS_TOKEN, wait=3):
        self._wait = wait
        self._api = API_URL
        self._web = WEB_URL
        self._access_token = GENIUS_TOKEN
        self._session = requests.Session()
        self._session.headers = {
            'Authorization': 'Bearer ' + self._access_token}

    @property
    def wait(self):
        """Sets or gets wait value """
        return self._wait
    
    @wait.setter
    def wait(self, value):
        self._wait = value

    @property
    def api_url(self):
        """Gets url of api"""
        return self._api
    
    @property
    def web_url(self):
        """Gets url of web api """
        return self._web

    def search(self, artist_name, page=1, per_page=5):
        '''Search Genius' web API for artist name
        
        Given name of artist, sends an API request and 
        parses JSON data to find relevant output.

        Performs a search on the Genius database to 
        return a name and ID if match is successful.

        This method is needed since a user's spelling might
        not match the name stored in Genius' database.For 
        example, 'Tupac' is spelled '2Pac' in Genius
        directory.

        Args:
            artist_name: search query for artist name (str)
            page: current page (int) (optional)
            per_page: max number of results to return per request (int) (optional)        
        
        Returns:
            (artist, artist_id): tuple of artist and id retrieved from Genius database
                                (str, int)
        '''

        artists = list()
        artists_data = list()
        payload = {'per_page': per_page, 'page': page, 'q': artist_name}
        url = WEB_URL + 'search/multi?'
        api_response = requests.get(url, params=payload, timeout=self.wait)
        json_data = api_response.json(
            ) if api_response and api_response.status_code == 200 else None
        # parsing
        if json_data is not None:
            for n in json_data['response']['sections']:
                for hit in n['hits']:
                    if hit['result']['_type'] == 'artist':
                        artists_data.append(hit['result'])
                        artists.append(hit['result']['name'])
            artist, artist_id = artists_data[0]['name'], artists_data[0]['id']
            return artist, artist_id
        else:
            return api_response.status_code

    def search_song(self, artist_name, artist_id, page=1, per_page=20):
        ''' Searches for artist's top 20 songs based on popularity
        
        If found on the database, up to 20 songs are returned from a single request.
        
        NOTE:
            artist_name and artist_id must be accurate, use
            search method before calling this function

        Args:
            artist_name: EXACT artist name (str)
            artist_id: EXACT artist ID (str)
            page: current page (int) (optional)
            per_page: max number of results to return per request (int) (optional)

        Returns:
            if api_response.status_code == 200:
                (songs, songs_data): tuple of songs and songs_data in list format 
                                 retrieved from Genius database (list, list)
            else:
                api_response.status_code: error code pertaining to request (int)
              
        '''
        songs = list()
        songs_data = list()
        url = API_URL + 'search?'
        payload = {
            'q': artist_name,
            'sort': 'popularity',
            'per_page': per_page,
            'page': page}
        api_response = self._session.request(
            'GET', url, params=payload, timeout=self.wait)
        json_data = api_response.json(
            ) if api_response and api_response.status_code == 200 else None
        # parse JSON data
        if json_data is not None:
            for hits in json_data['response']['hits']:
                if hits['type'] == 'song':
                    song_name = hits['result']['title']
                    primary_artist_id = hits['result']['primary_artist']['id']
                    if (
                        any(
                            x in song_name.lower(
                                ) for x in SKIP
                                ) is False
                                ) and (artist_id == primary_artist_id):
                        songs_data.append(hits['result'])
                        songs.append(song_name)
            return songs, songs_data
        else:
            return api_response.status_code

    def get_all_songs(self, artist_name, artist_id, return_data=False):
        '''Searches for artist's top 100 (max) songs based on popularity

        If found on the database, up to 20 songs are returned from a single request.

        NOTE:
            artist_name and artist_id must be accurate, use
            search method before calling this function

        Args:
            artist_name: EXACT artist name (str)
            artist_id: EXACT artist ID (str)
            page: current page (int) (optional)
            per_page: max number of results to return per request (int) (optional)
            return_data: whether to return song data (bool)

        Returns:
            if return_data:
                (songs, songs_data): tuple of songs and songs_data in list format 
                                 retrieved from Genius database (list, list)     
            else:
                songs: (list)
        '''

        all_songs = list()
        all_songs_data = list()
        # sends multiple requests
        for i in range(1, 6):
            songs, song_data = self.search_song(artist_name, artist_id, page=i)
            all_songs += songs
            all_songs_data += song_data

        if return_data:
            return all_songs, all_songs_data

        else:
            return all_songs

    def get_song_lyrics(self, song_data):
        '''Fetches songs lyrics 
        
        NOTE: Call search_songs or get_all_songs to get song data

        Args:
            song_data: (list)
        
        Returns:
            lyrics: lyrics of the songs (str)
        '''

        url = song_data['url']
        lyrics_page = requests.get(url)
        lyrics_page_html = bs(
            lyrics_page.content, 'html.parser'
            ) if lyrics_page.status_code == 200 else None

        if lyrics_page_html:
            lyrics = lyrics_page_html.find("div", {"class": "lyrics"})
            return lyrics.get_text()
