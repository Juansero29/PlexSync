from plexapi.myplex import MyPlexAccount
from plexapi.exceptions import BadRequest
from plexapi.server import PlexServer
from dotenv import load_dotenv
import os
from xml.etree import ElementTree
import requests

PLEX_TOKEN = os.getenv("PLEX_TOKEN")
PLEX_USERNAME = os.getenv("PLEX_USERNAME")
PLEX_SERVER_ADDRESS = os.getenv("PLEX_SERVER_ADDRESS")

# Load environment variables
load_dotenv()

class PlexClient:
    def __init__(self, plexUsername, plexToken):
        """Initialize with an authenticated Plex account."""
        self.account = MyPlexAccount(plexUsername, token=plexToken)
        self.plex = PlexServer(PLEX_SERVER_ADDRESS, PLEX_TOKEN)

    def search_media_in_plex(self, title, year, content_type):
        """Search for a movie or TV show in Plex's catalog using the searchDiscover method."""
        try:
            # Search Plex Discover for the given title and content type
            results = self.account.searchDiscover(title, libtype=content_type)

            # Check if any results are returned
            if not results:
                print(f"No results found for {title} ({year}) in Plex Discover.")
                return None

            # Look for the exact match based on year
            for result in results:
                if result.year == year:
                    print(f"Found media: {result.title} ({result.year})")
                    return result  # Return the media object itself (with ratingKey)

            print(f"No exact match found for {title} ({year}).")
            return None

        except Exception as e:
            print(f"Error searching for {title} ({year}) in Plex Discover: {e}")
            return None

    def add_to_plex_watchlist(self, plex_media):
        """Add a movie or TV show to the Plex watchlist using its media object."""
        try:
            # Add to Plex watchlist
            self.account.addToWatchlist(plex_media)
            print(f"Successfully added {plex_media.title} ({plex_media.year}) to the Plex watchlist.")

        except BadRequest as e:
            print(f"Bad request: {e}")
        except NotFound as e:
            print(f"Not found: {e}")
        except Exception as e:
            print(f"Error adding media with Plex ID {plex_media.guid} to watchlist: {e}")

    def fetch_plex_watchlist(self):
            """Fetches the current watchlist from Plex."""
            try:
                # Retrieve the user's watchlist
                watchlist = self.account.watchlist()
                print("Plex Watchlist:")
                
                # Display each item in the watchlist
                for item in watchlist:
                    # Fetch user state (this will include the date when the item was added to the watchlist)
                    user_state = self.account.userState(item)
                    item.added_at = user_state.watchlistedAt if user_state.watchlistedAt else "Unknown"
                    
                    print(f"- {item.title} ({item.year}) Added to Watchlist at {item.added_at}")
                    
                return watchlist
            
            except Exception as e:
                print(f"Error fetching Plex watchlist: {e}")

    def remove_from_plex_watchlist(self, plex_media):
        """Remove a movie or TV show from the Plex watchlist using its media object."""
        try:
            # Remove from Plex watchlist using the media's ratingKey
            self.account.removeFromWatchlist(plex_media)
            print(f"Successfully removed {plex_media.title} ({plex_media.year}) from the Plex watchlist.")

        except BadRequest as e:
            print(f"Bad request: {e}")
        except NotFound as e:
            print(f"Not found: {e}")
        except Exception as e:
            print(f"Error removing media with Plex ID {plex_media.guid} from watchlist: {e}")
            
    def get_user_rated_content(self):
        """Retrieve all films, series, and episodes with ratings from Plex."""
        rated_media = []

        # Step 1: Search for rated movies
        movies = self.plex.library.section('Movies').search(userRating__exists=True)  # Search for movies with a rating
        for movie in movies:
            rated_media.append({
                'id': movie.ratingKey,
                'title': movie.title,
                'year': movie.year,
                'type': 'movie',
                'rating': movie.userRating
            })
            
        # Step 2: Search for rated TV Shows
        tv_shows = self.plex.library.section('TV Shows').search(userRating__exists=True) 
        for tv_show in tv_shows:
            if tv_show.userRating is not None:  # If the TV show itself has a rating
                rated_media.append({
                    'id': tv_show.ratingKey,
                    'title': tv_show.title,
                    'year': tv_show.year,
                    'type': 'tvshow',
                    'rating': tv_show.userRating
                })

        # Step 2.5: Fetch rated seasons using HTTP request
        url = f"{PLEX_SERVER_ADDRESS}/library/sections/1/all?type=3&userRating>=1&X-Plex-Token={PLEX_TOKEN}"  # Type 2 for seasons
        response = requests.get(url)

        if response.status_code == 200:
            # Parse the XML response for rated seasons
            tree = ElementTree.fromstring(response.content)
            
            # Find all season elements (Season videos)
            seasons = tree.findall(".//Directory")
            
            for season in seasons:
                title = season.get("title")
                year = season.get("year")
                rating = season.get("userRating")
                rating_key = season.get("ratingKey")
                season_index = season.get("index")
                parent_show_title = season.get("parentTitle", "Unknown TV Show")  # Fetch parent show title
                
                rated_media.append({
                    'id': rating_key,
                    'title': f"{parent_show_title} - S{str(season_index).zfill(2)}",
                    'year': year,
                    'type': 'season',
                    'rating': rating
                })

        # Step 3: Fetch rated episodes using HTTP request
        url = f"{PLEX_SERVER_ADDRESS}/library/sections/1/all?type=4&userRating>=1&X-Plex-Token={PLEX_TOKEN}"
        response = requests.get(url)
        
        if response.status_code == 200:
            # Parse the XML response for rated episodes
            tree = ElementTree.fromstring(response.content)
            
            # Find all episode elements (Video elements)
            episodes = tree.findall(".//Video")
            
            for episode in episodes:
                title = episode.get("title")
                year = episode.get("year")
                rating = episode.get("userRating")
                rating_key = episode.get("ratingKey")
                season = episode.get("parentIndex")
                episode_index = episode.get("index")
                parent_show_title = episode.get("grandparentTitle", "Unknown TV Show")  # Fetch parent show title
                
                rated_media.append({
                    'id': rating_key,
                    'title': f"{parent_show_title} - S{str(season).zfill(2)}E{str(episode_index).zfill(2)} - {title}",
                    'year': year,
                    'type': 'episode',
                    'rating': rating
                })

        return rated_media