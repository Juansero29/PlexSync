from .senscritique_gql_client import SensCritiqueGqlClient
from datetime import datetime

class SensCritiqueClient:
    def __init__(self, email, password, userId):
        """Initialize the client with a valid email and password."""
        self.client = SensCritiqueGqlClient.build(email, password)
        self.userId = userId

    # Function to translate French month to English
    def parse_french_date(self, date_str):
        
        months_in_french = {
            'janvier': 'January', 'février': 'February', 'mars': 'March', 'avril': 'April', 'mai': 'May',
            'juin': 'June', 'juillet': 'July', 'août': 'August', 'septembre': 'September', 'octobre': 'October',
            'novembre': 'November', 'décembre': 'December'
        }
        
        english_date = None
        
        for french_month, english_month in months_in_french.items():
            if french_month in date_str:
                english_date = date_str.replace(french_month, english_month)
                break
                
        try:
            parsed_date = datetime.strptime(english_date, "%d %B %Y")
            return parsed_date
        except Exception as e:
            print(f"Failed to parse using strptime: {e}")


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
                    title
                    year_of_production
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
        
        # Check if the response contains the expected data
        if "data" in response:
            user = response["data"]["user"]
            user_wishes = []  # Initialize an empty list to store the media information
            
            # Loop through the user's wishes and format the data
            for wish in user["wishes"]:
                title = wish.get("title", "Unknown Title")
                year = wish.get("year_of_production", "Unknown Year")
                genres = ", ".join(wish.get("genres", []))
                
                release_date_text = wish.get("release_date", "Unknown Release Date")

                release_date = self.parse_french_date(release_date_text)
            
                universe = wish.get("universe", "Unknown Universe")
                picture = wish["medias"].get("picture", "No picture available")
                
                # Store the media details in the user_wishes list
                media = {
                    "title": title,
                    "year": year,
                    "genres": genres,
                    "release_date": release_date,
                    "universe": universe,
                    "picture": picture
                }
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
        """Fetch media by title, year, and universe."""
        
        # Updated GraphQL query to fetch additional details like genres, release_date, universe, and picture
        query = """
        query SearchMedia($keywords: String!, $universe: String) {
            searchResult(keywords: $keywords, universe: $universe, limit: 5) {
                results {
                    products_list {
                        id
                        title
                        year_of_production
                        genres
                        release_date
                        universe
                        medias(pictureSize: "150") {
                            picture
                        }
                    }
                }
            }
        }
        """
        
        variables = {"keywords": title, "universe": universe}
        response = await self.client.request(query, variables)

        print(response)
        
        # Ensure we are checking the 'data' key
        if "data" in response and "searchResult" in response["data"]:
            results = response["data"]["searchResult"]["results"]
            for result in results:
                products_list = result.get("products_list", [])
                for product in products_list:
                    # Check if the 'year_of_production' matches
                    if product["year_of_production"] == year:
                        print(f"Found media: {product['title']} ({product['year_of_production']})")
                        print(f"Genres: {', '.join(product.get('genres', []))}")
                        print(f"Release Date: {product.get('release_date', 'Unknown')}")
                        print(f"Universe: {product.get('universe', 'Unknown')}")
                        picture = product["medias"].get("picture", "No picture available")
                        print(f"Picture: {picture}")
                        return product

                    # If year doesn't match, check release_date
                    release_date = product.get("release_date", None)
                    if release_date:
                        try:
                            # Parse the French release date string to datetime object
                            release_date = self.parse_french_date(release_date)
                            if release_date.year == year:
                                print(f"Found media by release year: {product['title']} ({release_date.year})")
                                print(f"Genres: {', '.join(product.get('genres', []))}")
                                print(f"Release Date: {release_date}")
                                print(f"Universe: {product.get('universe', 'Unknown')}")
                                picture = product["medias"].get("picture", "No picture available")
                                print(f"Picture: {picture}")
                                return product
                        except ValueError:
                            print(f"Could not parse release date: {release_date}")

        print(f"No media found for '{title}' ({year}).")
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
    

