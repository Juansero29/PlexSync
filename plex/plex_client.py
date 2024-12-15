from plexapi.myplex import MyPlexAccount
from plexapi.exceptions import BadRequest

class PlexClient:
    def __init__(self, plexUsername, plexToken):
        """Initialize with an authenticated Plex account."""
        self.account = MyPlexAccount(plexUsername, token=plexToken)

    def search_movie_in_plex(self, title, year, content_type):
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
                print(f"- {item.title} ({item.year})")
        
        except Exception as e:
            print(f"Error fetching Plex watchlist: {e}")