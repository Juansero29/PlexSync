from plexapi.myplex import MyPlexAccount
from plexapi.exceptions import BadRequest
from plexapi.server import PlexServer
from dotenv import load_dotenv
import os

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
        """Retrieve all films, series, and episodes with ratings from Plex more efficiently."""
        rated_media = []

        # Get all movies with a rating from the 'Movies' section
        movies_section = self.plex.library.section('Movies')
        movies = movies_section.search(userRating__exists=True)  # This filters for media with ratings
        for movie in movies:
            rated_media.append({
                'id': movie.ratingKey,
                'title': movie.title,
                'year': movie.year,
                'type': 'movie',
                'rating': movie.userRating
            })

        # Get all TV Shows with a rating from the 'TV Shows' section
        tv_shows_section = self.plex.library.section('TV Shows')
        tv_shows = tv_shows_section.search(userRating__exists=True)  # Filter TV Shows with ratings
        for tv_show in tv_shows:
            rated_media.append({
                'id': tv_show.ratingKey,
                'title': tv_show.title,
                'year': tv_show.year,
                'type': 'tvshow',
                'rating': tv_show.userRating
            })

            # Get all episodes of each TV Show with a rating
            episodes = tv_show.episodes()
            for episode in episodes:
                if episode.userRating is not None:
                    rated_media.append({
                        'id': episode.ratingKey,
                        'title': f"{tv_show.title} - {episode.title}",
                        'year': episode.year,
                        'type': 'episode',
                        'rating': episode.userRating
                    })

        return rated_media
