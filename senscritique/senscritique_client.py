# senscritique_client.py
from .senscritique_gql_client import SensCritiqueGqlClient


class SensCritiqueClient:
    def __init__(self, email, password, userId):
        """Initialize the client with a valid email and password."""
        self.client = SensCritiqueGqlClient.build(email, password)
        self.userId = userId


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
        
        if "data" in response:
            user = response["data"]["user"]
            print(f"User ID: {user['id']}")
            print(f"User Avatar: {user['medias']['avatar']}")
            print("Wishes:")
            for wish in user["wishes"]:
                title = wish.get("title", "Unknown Title")
                year = wish.get("year_of_production", "Unknown Year")
                genres = ", ".join(wish.get("genres", []))
                release_date = wish.get("release_date", "Unknown Release Date")
                universe = wish.get("universe", "Unknown Universe")
                picture = wish["medias"].get("picture", "No picture available")
                
                print(f"- {title} ({year})")
                print(f"  Genres: {genres}")
                print(f"  Release Date: {release_date}")
                print(f"  Universe: {universe}")
                print(f"  Picture: {picture}")
        else:
            print("Error fetching user wishes: User not found.")


    async def fetch_media_id(self, title, year, universe): 
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

        # Ensure we are checking the 'data' key
        if "data" in response and "searchResult" in response["data"]:
            results = response["data"]["searchResult"]["results"]
            for result in results:
                products_list = result.get("products_list", [])
                for product in products_list:
                    # Check if the year matches and then print the details
                    if product["year_of_production"] == year:
                        print(f"Found media: {product['title']} ({product['year_of_production']})")
                        print(f"Genres: {', '.join(product.get('genres', []))}")
                        print(f"Release Date: {product.get('release_date', 'Unknown')}")
                        print(f"Universe: {product.get('universe', 'Unknown')}")
                        # Accessing picture directly since 'medias' is an object, not a list
                        picture = product["medias"].get("picture", "No picture available")
                        print(f"Picture: {picture}")
                        return product["id"]

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
