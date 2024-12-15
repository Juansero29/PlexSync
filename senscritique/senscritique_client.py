# senscritique_client.py
from .senscritique_gql_client import SensCritiqueGqlClient


class SensCritiqueClient:
    def __init__(self, email, password):
        """Initialize the client with a valid email and password."""
        self.client = SensCritiqueGqlClient.build(email, password)

    def fetch_media_id(self, title, year, universe):
        """Fetch media by title, year, and universe."""
        query = """
            query SearchMedia($keywords: String!, $universe: String) {
                searchResult(keywords: $keywords, universe: $universe, limit: 5) {
                    results {
                        products_list {
                            id
                            title
                            year_of_production
                        }
                    }
                }
            }
        """
        variables = {"keywords": title, "universe": universe}
        response = self.client.raw_request(query, variables)

        for result in response["searchResult"]["results"][0]["products_list"]:
            if result["year_of_production"] == year:
                print(f"Found media: {result['title']} ({result['year_of_production']})")
                return result["id"]
        print(f"No media found for '{title}' ({year}).")
        return None

    def add_media_to_wishlist(self, media_id):
        """Add a media item to the SensCritique wishlist."""
        mutation = """
            mutation AddToWishlist($productId: Int!) {
                productWish(productId: $productId)
            }
        """
        try:
            self.client.raw_request(mutation, {"productId": media_id})
            print(f"Successfully added media {media_id} to the wishlist.")
        except Exception as e:
            print(f"Error adding media {media_id} to wishlist: {e}")

    def fetch_user_wishes(self, limit=30):
            """Fetch the wishlist of the authenticated user."""
            query = """
                query UserWishes($limit: Int) {
                    user {
                        id
                        medias {
                            avatar
                        }
                        wishes(limit: $limit) {
                            title
                            year_of_production
                            genres
                            release_date
                            universe
                            medias {
                                picture
                            }
                        }
                    }
                }
            """
            variables = {"limit": limit}
            response = self.client.raw_request(query, variables)

            if "user" in response:
                user = response["user"]
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