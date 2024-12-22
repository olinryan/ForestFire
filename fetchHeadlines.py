#!/usr/bin/env python
import requests
from dotenv import load_dotenv
import os

# Load .env file into environment variables
load_dotenv()

def fetch_headlines(option, top_headlines=5):
    """
    Fetch top headlines from the New York Times API for a specific category.
    
    :param option(s): The category of news. The possible section value are: 
        arts, automobiles, books/review, business, fashion, food, health, 
        home, insider, magazine, movies, nyregion, obituaries, opinion, politics, 
        realestate, science, sports, sundayreview, technology, theater, t-magazine, 
        travel, upshot, us, and world.
    :param top_headlines: Number of top headlines to fetch (default is 5).
    :return: A string containing the top headlines joined by '. ' or an error message.
    """
    headlines = []
    if isinstance(option,str):
        url = f"https://api.nytimes.com/svc/topstories/v2/{option}.json?api-key={os.getenv('NYT_API_KEY')}"

        try:
            # Send GET request
            response = requests.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

            # Parse the JSON response
            data = response.json()
            headlines = [item['title'] for item in data['results'][:top_headlines]]
            return '. '.join(headlines)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching headlines: {e}")
            return "-- ERROR --"
        
    elif isinstance(option,list):
        for option_x in option:
            url = f"https://api.nytimes.com/svc/topstories/v2/{option_x}.json?api-key={os.getenv('NYT_API_KEY')}"

            try:
                # Send GET request
                response = requests.get(url)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

                # Parse the JSON response
                data = response.json()
                headlines += [item['title'] for item in data['results'][:top_headlines]]

            except requests.exceptions.RequestException as e:
                print(f"Error fetching headlines: {e}")
                # headlines +=  "-- ERROR --"
        return '. '.join(headlines) + ". "
    
# Example usage
if __name__ == "__main__":
    category = "technology"  # Change to the desired category
    print(fetch_headlines(category))
