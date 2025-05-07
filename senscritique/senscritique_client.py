from .senscritique_gql_client import SensCritiqueGqlClient
from datetime import datetime
import os
import asyncio
from dotenv import load_dotenv
from plex.plex_client import PlexClient
import json
import re
# Load environment variables
load_dotenv()

SC_EMAIL = os.getenv("SC_EMAIL")
SC_PASSWORD = os.getenv("SC_PASSWORD")
SC_USER_ID = os.getenv("SC_USER_ID")
SC_USERNAME = os.getenv("SC_USERNAME")

class SensCritiqueClient:
    def __init__(self):
        """Initialize the client with a valid email and password."""
        self.client = SensCritiqueGqlClient.build(SC_EMAIL, SC_PASSWORD)
        self.userId = SC_USER_ID

    def parse_french_date(self, date_str):
        """Parse either ISO (YYYY-MM-DD) or French-formatted dates like '21 mars 2024'."""
        
        # Handle ISO date format directly
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            pass

        # Fallback for French month names
        months_in_french = {
            'janvier': 'January', 'février': 'February', 'mars': 'March', 'avril': 'April', 'mai': 'May',
            'juin': 'June', 'juillet': 'July', 'août': 'August', 'septembre': 'September', 'octobre': 'October',
            'novembre': 'November', 'décembre': 'December'
        }

        english_date = date_str
        for fr, en in months_in_french.items():
            if fr in date_str:
                english_date = date_str.replace(fr, en)
                break

        # Try parsing English-formatted versions
        for fmt in ("%d %B %Y", "%Y", "%B %Y"):
            try:
                return datetime.strptime(english_date, fmt)
            except Exception:
                continue

        print(f"Failed to parse date: {date_str}")
        return None

    async def fetch_user_wishes(self, limit=30):
        """Fetch the wishlist of the authenticated user."""
        
        query = """
        query UserWishes($id: Int!, $limit: Int) {
            user(id: $id) {
                id
                medias(avatarSize: "30x30") {
                    avatar
                }
                wishes(limit: $limit) {
                    id
                    title
                    year_of_production
                    original_title
                    genres
                    release_date
                    universe
                    medias(pictureSize: "150") {
                        picture
                    }
                }
            }
        }
        """
        
        variables = {"id": self.userId, "limit": limit}
        
        response = await self.client.request(query, variables)
        
        print("SensCritique watchlist:")
        
        # Check if the response contains the expected data
        if "data" in response:
            user = response["data"]["user"]
            user_wishes = []  # Initialize an empty list to store the media information
            
            if(user["wishes"]):
                # Loop through the user's wishes and format the data
                for wish in user["wishes"]:
                    title = wish.get("title", "Unknown Title")
                    original_title = wish.get("original_title", "Unknown Original Title")
                    year = wish.get("year_of_production", "Unknown Year")
                    genres = ", ".join(wish.get("genres", []))
                    id = wish.get("id", "Unknown ID")
                    release_date_text = wish.get("release_date", "Unknown Release Date")

                    release_date = self.parse_french_date(release_date_text)
            
                    date_wishlisted = await self.fetch_date_when_item_was_last_wishlisted_by_user(id)
        
                    universe = wish.get("universe", "Unknown Universe")
                    picture = wish["medias"].get("picture", "No picture available")
                    
                    # Store the media details in the user_wishes list
                    media = {
                        "id": id,
                        "date_wishlisted": date_wishlisted,
                        "title": title,
                        "original_title": original_title,
                        "year": year,
                        "genres": genres,
                        "release_date": release_date,
                        "universe": universe,
                        "picture": picture
                    }
                    
                    print(f"- {media['title']} ({media['release_date'].year}) Added to Wish List at {media['date_wishlisted']} - [{media['id']}]")

                    user_wishes.append(media)
                
                # Return the list of media
                return user_wishes
        else:
            print("Error fetching user wishes: User not found.")
            return []  

    async def fetch_media_id(self, title, year, universe):
        media = await self.fetch_media(title, year, universe)
        if media:
            return media["id"]
        else:
            return None
    
    async def fetch_media(self, title, year, universe):
        
        if isinstance(universe, str):
            universe = self.get_sc_media_type_id_from_plex_text_type(universe)
        
        if universe == 1 or universe == 4:
            return await self.fetch_media_tvShow_or_movie(title, year, universe)
        if universe == 32:
            return await self.fetch_episode(title, year)
            
        if universe == 5:
            return await self.fetch_season(title, year)
            
    
    async def fetch_media_tvShow_or_movie(self, title, year, universe):
        """Fetch media by title, year, and universe using SearchAutocomplete."""
        
        query = """
        query SearchAutocomplete($keywords: String!, $universe: String, $limit: Int) {
            searchAutocomplete(keywords: $keywords, universe: $universe, limit: $limit) {
                total
                items {
                    product {
                        id
                        title
                        originalTitle
                        universe
                        dateRelease
                        dateReleaseOriginal
                        medias {
                            picture
                        }
                        url
                    }
                }
            }
        }
        """

        universe_label = self.get_sc_text_media_type_from_sc_id(universe)
        variables = {
            "keywords": title,
            "universe": universe_label,
            "limit": 20
        }

        response = await self.client.request(query, variables)

        if "data" in response and "searchAutocomplete" in response["data"]:
            items = response["data"]["searchAutocomplete"]["items"]
            for item in items:
                product = item.get("product")
                if not product:
                    continue

                # Check universe match (as string or int, depending on API)
                if str(product.get("universe")) != str(universe):
                    continue

                # Try matching by exact title and year of release
                product_title = product.get("title", "")
                product_year = None

                # Parse release year from available date fields
                for date_field in ("dateRelease", "dateReleaseOriginal"):
                    release_date = product.get(date_field)
                    if release_date:
                        try:
                            product_year = self.parse_french_date(release_date).year
                            break
                        except Exception:
                            pass

                if product_year:
                    if (
                        product_year == year
                        or str(year) in product_title
                        or (product_year in {year - 1, year + 1} and product_title == title)
                    ):
                        print(f"Found media: {product_title} ({product_year})")
                        print(f"Universe: {product.get('universe')}")
                        print(f"URL: {product.get('url')}")
                        print(f"Picture: {product['medias'].get('picture', 'No picture')}")
                        product['year_of_production'] = product_year
                        return product

        print(f"No media found for '{title}' ({year}) in SensCritique")
        return None

    async def fetch_episode(self, title, year):
        try:
            # Step 1: Extract episode info
            episode_info = self.get_episode_info_from_title(title, year)
            if not episode_info:
                raise ValueError("Could not parse episode information from the title.")

            tv_show_name = episode_info["tv_show_name"]
            season_number = episode_info["season_number"]
            episode_number = episode_info["episode_number"]

            print(f"Searching for TV show: {tv_show_name}, Season: {season_number}, Episode: {episode_number}")

            # Step 2: Fetch the TV show (type 4 indicates TV show in your system)
            tv_show = await self.fetch_media_tvShow_or_movie(tv_show_name, year, 4)
            if not tv_show:
                raise ValueError(f"TV show '{tv_show_name}' not found.")

            tv_show_id = tv_show["id"]  # Extract TV show ID
            print(f"Found TV show '{tv_show_name}' with ID: {tv_show_id}")

            # Step 3: GraphQL query for seasons and episodes
            query = """
            query FetchTvShowWithEpisodes($id: Int!) {
            product(id: $id) {
                id
                title
                seasons {
                id
                seasonNumber
                episodes {
                    id
                    episodeNumber
                    title
                }
                }
            }
            }
            """

            # Step 4: Set the query variables
            variables = {
                "id": tv_show_id
            }

            # Step 5: Send the query request
            response = await self.client.request(query, variables)

            # Step 6: Process the response
            if not response or response.get("errors"):
                raise ValueError(f"Error fetching TV show details: {response.get('errors')}")

            seasons = response.get("data", {}).get("product", {}).get("seasons", [])

            # Step 7: Find the correct episode
            for season in seasons:
                if season["seasonNumber"] == season_number:
                    for episode in season["episodes"]:
                        if episode["episodeNumber"] == episode_number:
                            print(f"Found Episode: {episode['title']} (ID: {episode['id']})")
                            return {
                                "id": episode["id"],
                                "title": episode["title"],
                                "season": season_number,
                                "episode": episode_number,
                                "year_of_production":  tv_show["year_of_production"]
                            }

            print("Episode not found.")
            return None

        except Exception as e:
            print(f"Error in fetch_episode: {e}")
            return None

    async def fetch_season(self, title, year):
        """
        Fetches a specific season from SensCritique based on title and year.

        Args:
            title (str): Structured title, e.g., "Happy Tree Friends - Season 1" or "Monster (2022) - The Jeffrey Dahmer Story".
            year (str): Year of the TV show.

        Returns:
            dict: Information about the matched season, including its ID.
        """
        try:
            # Step 1: Extract TV show name and season title/number
            tv_show_name, season_number, season_title = self._extract_season_info(title)
            print(f"Extracted TV Show Name: '{tv_show_name}', Season Number: '{season_number}', Season Title: '{season_title}'")

            # Step 2: Fetch the TV show
            tv_show = await self.fetch_media_tvShow_or_movie(tv_show_name, year, 4)
            if not tv_show:
                raise ValueError(f"TV show '{tv_show_name}' not found.")

            tv_show_id = tv_show["id"]  # Extract TV show ID
            print(f"Found TV show '{tv_show_name}' with ID: {tv_show_id}")

            # Step 3: GraphQL query for seasons
            query = """
            query FetchTvShowSeasons($id: Int!) {
                product(id: $id) {
                    id
                    title
                    seasons {
                        id
                        seasonNumber
                        title
                    }
                }
            }
            """

            # Step 4: Set query variables
            variables = {"id": tv_show_id}

            # Step 5: Send the query request
            response = await self.client.request(query, variables)

            # Step 6: Process the response
            if not response or response.get("errors"):
                raise ValueError(f"Error fetching TV show seasons: {response.get('errors')}")

            seasons = response.get("data", {}).get("product", {}).get("seasons", [])

            # Step 7: Match the season by number or title
            for season in seasons:
                if season_number and season.get("seasonNumber") == season_number:
                    print(f"Found Season: {season['title']} (ID: {season['id']})")
                    return {
                        "id": season["id"],
                        "title": season["title"],
                        "season": season_number,
                        "year_of_production": tv_show["year_of_production"]
                    }
                elif season_title and season.get("title") == season_title:
                    print(f"Found Season by Title: {season['title']} (ID: {season['id']})")
                    return {
                        "id": season["id"],
                        "title": season["title"],
                        "season": season.get("seasonNumber"),
                        "year_of_production": tv_show["year_of_production"]
                    }

            print("Season not found.")
            return None

        except Exception as e:
            print(f"Error in fetch_season: {e}")
            return None

    # Helper function to extract season info
    def _extract_season_info(self, title):
        """
        Extract the TV show name, season number, and season title from the input title.

        Args:
            title (str): Input title, e.g., 
                        "Happy Tree Friends - Season 1",
                        "Happy Tree Friends - S02",
                        "Happy Tree Friends - Temporada 2",
                        "Happy Tree Friends - Saison 2".

        Returns:
            tuple: (tv_show_name, season_number, season_title)
        """
        try:
            # Step 1: Regex to match various season formats
            pattern = r"^(.*?)\s-\s(?:Season|Saison|Temporada|S)(?:\s?)(\d{1,2})\b"
            match = re.match(pattern, title, re.IGNORECASE)

            if match:
                tv_show_name = match.group(1).strip()  # Extract TV show name
                season_number = int(match.group(2))    # Extract season number
                return tv_show_name, season_number, None

            # Step 2: Fallback - Split the title by the first hyphen
            parts = title.split(" - ", 1)
            tv_show_name = parts[0].strip()
            season_title = parts[1].strip() if len(parts) > 1 else None
            return tv_show_name, None, season_title

        except Exception as e:
            print(f"Error extracting season info: {e}")
            return None, None, None        

    def get_episode_info_from_title(self, title, year):
        """
        Extract the TV show name, season number, and episode number from the structured title.

        Args:
            title (str): A structured title string, e.g., "Happy Tree Friends - S02E13 - I Get a Trick Out of You (2003)".
            year (str): The year of the episode.

        Returns:
            dict: A dictionary with the TV show name, season number, and episode number.
        """
        try:
            # Regular expression to match the format
            pattern = r"^(.*?)\s-\sS(\d{2})E(\d{2})\s-"

            # Match the pattern
            match = re.match(pattern, title)

            if match:
                tv_show_name = match.group(1).strip()  # Group 1: TV show name
                season_number = int(match.group(2))    # Group 2: Season number as int
                episode_number = int(match.group(3))   # Group 3: Episode number as int

                # Debugging output (optional)
                print(f"TV Show Name: {tv_show_name}")
                print(f"Season Number: {season_number}")
                print(f"Episode Number: {episode_number}")

                # Return extracted information
                return {
                    "tv_show_name": tv_show_name,
                    "season_number": season_number,
                    "episode_number": episode_number,
                    "year": year
                }
            else:
                raise ValueError("Title format is invalid. Expected format: 'TV Show - SxxExx - Episode Title (Year)'")

        except Exception as e:
            print(f"Error parsing title: {e}")
            return None
        
        

    async def add_media_to_wishlist(self, media_id):
            """Add a media item to the SensCritique wishlist."""
            mutation = """
                mutation AddToWishlist($productId: Int!) {
                    productWish(productId: $productId)
                }
            """
            try:
                await self.client.raw_request(mutation, {"productId": media_id})
                print(f"Successfully added media {media_id} to the wishlist.")
            except Exception as e:
                print(f"Error adding media {media_id} to wishlist: {e}")

    async def remove_media_from_wishlist(self, media_id):
        """Remove a media item from the SensCritique wishlist."""
        mutation = """
            mutation RemoveFromWishlist($productId: Int!) {
                productUnwish(productId: $productId)
            }
        """
        try:
            # Send the request with the mutation to remove the media from the wishlist
            await self.client.raw_request(mutation, {"productId": media_id})
            print(f"Successfully removed media {media_id} from the wishlist.")
        except Exception as e:
            print(f"Error removing media {media_id} from wishlist: {e}")

    async def fetch_from_user_collections(self, id):
            """Fetch a media from the user collections by its ID."""
            
            query = """
            query UserDiary($isDiary:Boolean, $limit:Int, $offset:Int, $universe:String, $username:String!, $yearDateDone:Int) {
                user(username:$username) {
                    collection(isDiary:$isDiary limit:$limit offset:$offset universe:$universe yearDateDone:$yearDateDone) {
                        products {
                            id
                            universe
                            dateCreation
                            dateLastUpdate
                            category
                            title
                            originalTitle
                            alternativeTitles
                            yearOfProduction
                            url
                            otherUserInfos(username:$username) {
                                dateDone
                                rating
                            }
                        }
                    }
                }
            }
            """

            # Set the variables for the query
            variables = {
                "isDiary": False,
                "limit": 5000,
                "offset": 0,
                "universe": None,
                "username": SC_USERNAME,  # Replace with the correct username if needed
                "yearDateDone": None
            }

            # Send the request using the GraphQL client
            response = await self.client.request(query, variables)
            
            # Check the response data
            if "data" in response and "user" in response["data"]:
                # Find the product with the matching ID
                products = response["data"]["user"]["collection"]["products"]
                for product in products:
                    if product["id"] == id:
                        return product  # Return the product's data

            print("No media found with the specified ID.")
            return None

    async def fetch_date_when_item_was_last_wishlisted_by_user(self, id):
            """Fetch the date when the item was last wishlisted."""
            query = """
            query Feed($limit: Int, $offset: Int, $productId: Int, $userId: Int, $excludeArchive: Boolean) { feed(limit: $limit, offset: $offset, productId: $productId, userId: $userId, excludeArchive: $excludeArchive) { feeds { dateCreation   isWishList product { id } } } }
            """
            
            variables = {
                "limit": 10,
                "offset": 0,
                "productId": id,
                "userId": int(self.userId),
                "excludeArchive": False
            }
            
            
            try:
                response = await self.client.request(query, variables)
                
                if response and 'data' in response and 'feed' in response['data']:
                    feeds = response['data']['feed'][0]['feeds']
                    for feed in feeds:
                        if feed['isWishList']:
                            # If the item is wishlisted, return the creation date
                            date_creation = feed['dateCreation']
                            return datetime.strptime(date_creation, "%Y-%m-%dT%H:%M:%S.%fZ")  # Parse the date
                
                return None  # Return None if no matching wishlisted item is found
            except Exception as e:
                print(f"Error fetching date: {e}")
                return None

    async def get_user_rated_media(self, limit=10000, offset=0):
        """Fetch all rated shows, seasons, and episodes from the user's collection."""
        
        # Define the updated query to fetch all rated media (movies, TV shows, seasons, and episodes)
        query = "query UserCollection($limit: Int, $offset: Int, $username: String!) { user(username: $username) { collection(limit: $limit, offset: $offset) { products { id originalTitle title universe category yearOfProduction currentUserInfos { rating dateDone } seasons { id universe originalTitle title seasonNumber currentUserInfos { rating dateDone } episodes { id episodeNumber universe originalTitle title currentUserInfos { rating dateDone } } } } } } }"
        
        # Define the variables
        variables = {
            "limit": limit,
            "offset": offset,
            "username": SC_USERNAME
        }

        # Send the request using the GraphQL client
        response = await self.client.request(query, variables)

        # Initialize a list to store the rated media
        rated_media = []

        # Check the response and process the products
        if "data" in response and "user" in response["data"]:
            products = response["data"]["user"]["collection"]["products"]

            # Iterate over the products and gather rated media
            for product in products:
                
                # If it's not a movie or a tv show, skip
                if product["universe"] not in [4, 1]:
                    continue
                
                # Check if the product has a rating
                if product["currentUserInfos"] and product["currentUserInfos"]["rating"] is not None:
                    rated_media.append({
                        "id": product["id"],
                        "title": product["originalTitle"] if product["originalTitle"] else product["title"],
                        "rating": product["currentUserInfos"]["rating"],
                        "type": self.get_plex_media_type_from_sc_id(product["universe"]),  # "movie", "tvshow", etc.
                        "category": product["category"],
                        "year": product["yearOfProduction"],
                        "ratedDate": product["currentUserInfos"]["dateDone"]
                    })

                # If it's a TV show, check its seasons and episodes for ratings
                if "seasons" in product and product["seasons"]:
                    for season in product["seasons"]:
                        season_title = season["originalTitle"] if season["originalTitle"] else season["title"]
                        if season["currentUserInfos"] and season["currentUserInfos"]["rating"] is not None:
                            rated_media.append({
                                "id": season["id"],
                                "title": season_title,
                                "rating": season["currentUserInfos"]["rating"],
                                "seasonNumber": season["seasonNumber"],
                                "type": "season",
                                "category": product["category"],
                                "year": product["yearOfProduction"],
                                "ratedDate": product["currentUserInfos"]["dateDone"]
                            })
                        
                        if "episodes" in season and season["episodes"]:
                            # Check episodes in this season
                            for episode in season["episodes"]:
                                if episode["currentUserInfos"] and episode["currentUserInfos"]["rating"] is not None:
                                    
                                    episode_title = episode["originalTitle"] if episode["originalTitle"] else episode["title"],
                                    rated_media.append({
                                        "id": episode["id"],
                                        "title": f"{season_title} - S{str(season['seasonNumber']).zfill(2)}E{str(episode['episodeNumber']).zfill(2)} - {episode_title}",
                                        "rating": episode["currentUserInfos"]["rating"],
                                        "type": "episode",
                                        "category": product["category"],
                                        "year": product["yearOfProduction"],
                                        "ratedDate": product["currentUserInfos"]["dateDone"]
                                    })
        
        return rated_media


    async def rate_media_with_id(self, media_id, rating):
            """Rate a media product with a given rating."""
            
            # Define the GraphQL mutation
            query = """
            mutation ProductRate($productId: Int!, $rating: Int!, $formatId: Int) {
                productRate(productId: $productId, rating: $rating, formatId: $formatId) {
                    id
                    title
                    currentUserInfos {
                        dateDone
                        hasStartedReview
                        isCurrent
                        id
                        isDone
                        isListed
                        isRecommended
                        isReviewed
                        isWished
                        productId
                        rating
                        userId
                        numberEpisodeDone
                        lastEpisodeDone {
                            episodeNumber
                            id
                            season {
                                seasonNumber
                                id
                                episodes {
                                    title
                                    id
                                    episodeNumber
                                }
                            }
                        }
                        gameSystem {
                            id
                            label
                        }
                        review {
                            author {
                                id
                                name
                            }
                            url
                        }
                    }
                }
            }
            """
            
            # Prepare the variables for the mutation
            variables = {
                "productId": media_id,
                "rating": rating,
                "formatId": None  # You can pass a specific formatId if needed
            }

            # Send the request using your Apollo client
            response = await self.client.request(query, variables)
            
            # Process the response to return useful information
            if "data" in response and "productRate" in response["data"]:
                product_info = response["data"]["productRate"]
                rating_info = product_info["currentUserInfos"]
                
                print(f"Product {product_info['title']} [{product_info['id']}] has been rated! {rating_info['rating']}/10")
                
                # Return the rating and other relevant details
                return {
                    "mediaId": product_info["id"],
                    "rating": rating_info["rating"],
                    "userId": rating_info["userId"],
                    "dateDone": rating_info["dateDone"],
                    "isDone": rating_info["isDone"],
                    "isListed": rating_info["isListed"],
                    "isRecommended": rating_info["isRecommended"],
                    "isReviewed": rating_info["isReviewed"],
                    "isWished": rating_info["isWished"]
                }
                
            
            # If the response does not contain the expected data, handle the error
            else:
                raise Exception("Failed to rate the media. Response data is missing or malformed.")

    async def search_and_rate_media(self, title, year, content_type, rating):
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
        
        sc_media_type = self.get_sc_media_type_id_from_plex_text_type(content_type)
        
        
        media = await self.fetch_media(title, year, sc_media_type)

        if media:
            print(f"Rating media matched in SensCritique: {media['title']} ({media['year_of_production']}) [{content_type}]")
            await self.rate_media_with_id(media['id'], rating)
        else:
                print(f"Impossible to rate in SensCritique. No results found for {title} ({year}) [{content_type}].")

    def get_plex_media_type_from_sc_id(self, mediaTypeid):
        media_type_mapping = {
            1: "movie",
            4: "show",
            5: "season",
            32: "episode"
        }

        # Return the mapped value or None if mediaTypeid is not found
        media_type = media_type_mapping.get(mediaTypeid, None)
        return media_type

    def get_sc_media_type_id_from_plex_text_type(self, mediaTypeid):
        media_type_mapping = {
            "movie": 1,
            "show": 4,
            "season": 5,
            "episode": 32 
        }

        # Return the mapped value or None if mediaTypeid is not found
        media_type = media_type_mapping.get(mediaTypeid, None)
        return media_type
    
    def get_sc_text_media_type_from_sc_id(self, mediaTypeid):
        media_type_mapping = {
            1: "movie",
            4: "tvShow",
            5: "season",
            32: "episode"
        }

        # Return the mapped value or None if mediaTypeid is not found
        media_type = media_type_mapping.get(mediaTypeid, None)
        return media_type
    