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
    def __init__(self):
        """Initialize with an authenticated Plex account."""
        self.account = MyPlexAccount(PLEX_USERNAME, token=PLEX_TOKEN)
        self.plex = PlexServer(PLEX_SERVER_ADDRESS, PLEX_TOKEN)
        self.useruuid = None
  
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
                    
                    
                    item.frenchTitle = self.get_french_title(item.key, idIsKey=True)
                    
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
            
    def get_user_rated_content(self, frenchTitles=True):
        """Retrieve all films, series, seasons, and episodes with ratings from Plex Discover."""
        rated_media = []
        end_cursor = None  # To manage pagination

        headers = {
            "Host": "community.plex.tv",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Plex-Language": "fr",
            "X-Plex-Token": PLEX_TOKEN
        }

        graphql_query = """
        query GetReviewsHub($uuid: ID = "", $first: PaginationInt!, $after: String) {
        user(id: $uuid) {
            reviews(first: $first, after: $after) {
            nodes {
                ... on ActivityRating {
                ...ActivityRatingFragment
                }
                ... on ActivityWatchRating {
                ...ActivityWatchRatingFragment
                }
                ... on ActivityReview {
                ...ActivityReviewFragment
                }
                ... on ActivityWatchReview {
                ...ActivityWatchReviewFragment
                }
            }
            pageInfo {
                hasNextPage
                endCursor
            }
            }
        }
        }

        fragment ActivityRatingFragment on ActivityRating {
        id
        date
        rating
        metadataItem {
            id
            title
            type
            year
            index
            key
            parent {
            title
            year
            index
            }
            grandparent {
            title
            year
            index
            }
        }
        }

        fragment ActivityWatchRatingFragment on ActivityWatchRating {
        id
        date
        rating
        metadataItem {
            title
            type
            year
            index
            key
            parent {
            title
            year
            index
            }
            grandparent {
            title
            year
            index
            }
        }
        }

        fragment ActivityReviewFragment on ActivityReview {
        id
        date
        reviewRating: rating
        message
        hasSpoilers
        metadataItem {
            id
            title
            type
            year
            index
            key
            parent {
            title
            year
            index
            }
            grandparent {
            title
            year
            index
            }
        }
        }

        fragment ActivityWatchReviewFragment on ActivityWatchReview {
        id
        date
        reviewRating: rating
        message
        hasSpoilers
        metadataItem {
            id
            title
            type
            year
            index
            key
            parent {
            title
            year
            index
            }
            grandparent {
            title
            year
            index
            }
        }
        }
        """

        user_uuid = self.get_user_id_by_username(PLEX_USERNAME)

        while True:
            payload = {
                "query": graphql_query,
                "variables": {
                    "uuid": user_uuid,
                    "first": 100,
                    "after": end_cursor
                },
                "operationName": "GetReviewsHub"
            }

            response = requests.post("https://community.plex.tv/api", headers=headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                nodes = data.get("data", {}).get("user", {}).get("reviews", {}).get("nodes", [])
                page_info = data.get("data", {}).get("user", {}).get("reviews", {}).get("pageInfo", {})
                end_cursor = page_info.get("endCursor")
                has_next_page = page_info.get("hasNextPage")

                for node in nodes:
                    metadata = node.get("metadataItem", {})
                    rating = node.get("rating") or node.get("reviewRating")
                    reviewText = node.get("message", "").strip()
                    reviewHasSpoilers = node.get("hasSpoilers", False)
                    ratedDate = node.get("date")

                    if metadata and rating:
                        id = metadata.get("id")
                        item_type = metadata.get("type")

                        french_title = self.get_french_title(id) if frenchTitles else None
                        title = french_title if french_title else metadata.get("title")

                        year = metadata.get("year")
                        item = {
                            "id": id,
                            "title": title,
                            "type": item_type,
                            "year": year,
                            "rating": rating,
                            "ratedDate": ratedDate
                        }

                        if reviewText:
                            item["reviewText"] = reviewText
                            item["reviewHasSpoilers"] = reviewHasSpoilers

                        if item_type == "EPISODE":
                            parent = metadata.get("parent", {})
                            grandparent = metadata.get("grandparent", {})
                            season = parent.get("index")
                            episode = metadata.get("index")
                            item["tvShowYear"] = grandparent.get("year")
                            item["title"] = f"{grandparent.get('title', 'Unknown Show')} - S{str(season).zfill(2)}E{str(episode).zfill(2)} - {title}"
                        elif item_type == "SEASON":
                            parent = metadata.get("parent", {})
                            item["title"] = f"{parent.get('title', 'Unknown Show')} - Season {metadata.get('index')}"

                        rated_media.append(item)

                if not has_next_page:
                    break
            else:
                print(f"Failed to fetch rated content. Status: {response.status_code}, Response: {response.text}")
                break

        return rated_media

    def get_french_title(self, id, idIsKey=False):
        headers = {
                "Accept": "application/json",
                "Host": "discover.provider.plex.tv",
                "X-Plex-Language": "fr",
                "X-Plex-Token": PLEX_TOKEN
            }
        
        if idIsKey:
            url = f"https://discover.provider.plex.tv{id}"
        else:
            url = f"https://discover.provider.plex.tv/library/metadata/{id}"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            metadata = data.get("MediaContainer", {}).get("Metadata", {})
            
            if metadata:
                french_title = metadata[0].get("title", {})
                
                return french_title
                
                
        
    
    def rate_media_with_ratingKey(self, media, rating):
        
        """Rate a media product"""
        if media:
            print(f"Media found: {media.title} ({media.year}) with rating {media.ratingKey}")

            # Rate the media item using the rate() method of the plexapi library
            try:
                media.rate(rating)
                
                # Return the updated information
                return {
                    "id": media.ratingKey,
                    "title": media.title,
                    "rating": media.rating,
                    "userRating": media.userRating,
                    "year": media.year,
                    "type": media.type
                }
            except Exception as e:
                print(f"Error rating media: {e}")
        else:
            print("No media found!")
            raise ValueError("Media with the given guid not found.")

    def search_media_in_plex(self, title, year, content_type):
        """
        Search for any media in Plex globally, including those not in the server.

        Args:
            title (str): The title of the media to search for.
            year (int): The year of the media.
            content_type (str): The type of content ('movie' or 'show').

        Returns:
            dict: A dictionary representing the detailed media metadata with the ratingKey, or None if not found.
        """
        try:
            # Perform global search using searchDiscover
            results = self.account.searchDiscover(title, libtype=content_type)

            if not results:
                print(f"No results found for {title} ({year}) in Plex Discover.")
                return None

            # Look for the exact match based on year
            for result in results:
                if (year and result.year == year) or not year:
                    # Fetch detailed metadata to get the ratingKey
                    url = f"https://metadata.provider.plex.tv{result.key}"
                    params = {"X-Plex-Token": PLEX_TOKEN}
                    response = requests.get(url, params=params)

                    if response.status_code == 200:
                        tree = ElementTree.fromstring(response.text)
                        
                        video = tree.find(".//Video")
                        ratingKey = None
                        
                        if video:
                            ratingKey = video.get("ratingKey")
                        else:
                            directory = tree.find(".//Directory")
                            ratingKey = directory.get("ratingKey")
                            
                        
                        if ratingKey:
                            return {
                                "title": result.title,
                                "year": result.year,
                                "ratingKey": ratingKey
                            }
                    else:
                        print(f"Failed to fetch global metadata. Status code: {response.status_code}")
                        
            print(f"No match found for {title} ({year}).")
            return None

        except Exception as e:
            print(f"Error searching for {title} ({year}) in Plex Discover: {e}")
            return None
        
    def search_media_in_server(self, title, year, content_type):
        """
        Search for media in Plex based on title, year, and content type.

        Args:
            title (str): The title of the media to search for.
            year (int): The year of the media.
            content_type (str): The type of content ('movie' or 'show').

        Returns:
            plexapi.video.Video or None: The matching media object, or None if not found.
        """
        try:
            libraries = self.plex.library.sections()
            for library in libraries:
                if library.type in ['movie', 'show']:
                    results = library.search(title=title)

                    for media in results:
                        if media.title.lower() == title.lower() and media.year == year:
                            return media

            return None

        except Exception as e:
            print(f"Error searching for media: {e}")
            return None

    def rate_media(self, ratingKey, rating):
        """
        Rate a globally searched media item using its metadata ID.

        Args:
            ratingKey (str): The metadata ID (key) of the media to rate.
            rating (int): The rating value (1 to 10).

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # API endpoint for rating
            url = "https://discover.provider.plex.tv/actions/rate"

            # Headers for the request
            headers = {
                "Host": "discover.provider.plex.tv",
                "Accept": "application/json",
                "X-Plex-Token": PLEX_TOKEN
            }

            # Query parameters
            params = {
                "identifier": "tv.plex.provider.discover",
                "key": ratingKey,
                "rating": rating
            }

            # Send PUT request
            response = requests.put(url, headers=headers, params=params)

            # Check response status
            if response.status_code == 200:
                print(f"Successfully rated media with ID {ratingKey} as {rating} stars.")
                return True
            else:
                print(f"Failed to rate media. Status code: {response.status_code}, Response: {response.text}")
                return False

        except Exception as e:
            print(f"Error rating global media: {e}")
            return False

    def search_and_rate_media(self, title, year, content_type, rating, reviewText=None, reviewHasSpoilers=None):
        """
        Search for media locally and globally, then rate it.

        Args:
            title (str): The title of the media to search for.
            year (int): The year of the media.
            content_type (str): The type of content ('movie' or 'show').
            rating (int): The rating value (1 to 10).

        Returns:
            None
        """
        result = self.search_media_in_plex(title, year, content_type)

        if result:
            print(f"Found media: {result['title']} ({result['year']})")

            metadata_id = result['ratingKey']
            # Example: Rate the first result
            self.rate_media(metadata_id, rating)

        else:
            print(f"No results found for {title} ({year}) [{content_type}]")
    
    def get_user_id_by_username(self, username):
        """
        Retrieve the Plex user ID based on the username.
        
        Args:
            username (str): The Plex username to look up.
        
        Returns:
            str: The user ID if found, None otherwise.
        """
        
        if self.useruuid:
            return self.useruuid
        
        headers = {
            "Host": "community.plex.tv",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Plex-Token": PLEX_TOKEN
        }

        graphql_query = """
        query GetUserDetails($username: ID!) {
          userByUsername(username: $username) {
            id
            avatar
            username
            displayName
          }
        }
        """

        payload = {
            "query": graphql_query,
            "variables": {
                "username": username
            },
            "operationName": "GetUserDetails"
        }

        # Send the request
        response = requests.post("https://community.plex.tv/api", headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            user_data = data.get("data", {}).get("userByUsername")
            if user_data:
                print(f"Plex User '{username}' found. ID: {user_data['id']}")
                self.useruuid = user_data["id"]
                return self.useruuid
            else:
                print(f"Plex User '{username}' not found.")
                return None
        else:
            print(f"Failed to fetch user ID from Plex. Status: {response.status_code}, Response: {response.text}")
            return None

    def get_user_rated_content_in_local_plex_server(self):
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