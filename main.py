import os
import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from plexapi.myplex import MyPlexAccount
from plexapi.exceptions import BadRequest

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

PLEX_TOKEN = os.getenv("PLEX_TOKEN")
PLEX_USERNAME = os.getenv("PLEX_USERNAME")
SC_EMAIL = os.getenv("SC_EMAIL")
SC_PASSWORD = os.getenv("SC_PASSWORD")

DISCOVER_API_URL = "https://discover.provider.plex.tv/library/search"
WATCHLIST_API_URL = "https://metadata.provider.plex.tv/actions/watchlist"

# GraphQL Transport for SensCritique
graphql_endpoint = "https://your-graphql-endpoint"  # Replace with the actual SC GraphQL endpoint
sc_transport = RequestsHTTPTransport(
    url=graphql_endpoint,
    headers={"Authorization": f"Bearer {PLEX_TOKEN}"}
)
sc_client = Client(transport=sc_transport, fetch_schema_from_transport=True)


# 1. Fetch Plex Watchlist
def fetch_plex_watchlist():
    try:
        # Log into Plex account using the provided username and token
        account = MyPlexAccount(PLEX_USERNAME, token=PLEX_TOKEN)

        # Get the Plex server (we assume the first server, but you can choose a specific one)
        plex = account.resource("Plex Server").connect()

        # Get the watchlist from Plex (this may vary if you have multiple libraries)
        watchlist = plex.library.section('Movies').all()  # Change 'Movies' to the correct section for TV shows if needed

        # Display the watchlist
        if watchlist:
            print("Plex Watchlist:")
            for item in watchlist:
                print(f"- {item.title} ({item.year})")
        else:
            print("Your Plex watchlist is empty.")
        
    except BadRequest as e:
        print(f"Error fetching Plex watchlist: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# 2. Fetch SC Wishlist
def fetch_sc_wishlist():
    query = gql("""
        query UserWishes($avatarSize: String, $id: Int!, $limit: Int) {
            user(id: $id) {
                id
                wishes(limit: $limit) {
                    title
                    year_of_production
                }
            }
        }
    """)

    variables = {
        "avatarSize": "30x30",
        "id": 724296,  # Replace with your actual SC user ID
        "limit": 30
    }

    try:
        response = sc_client.execute(query, variable_values=variables)
        print("\nSensCritique Wishlist:")
        for wish in response["user"]["wishes"]:
            title = wish.get("title", "Unknown Title")
            year = wish.get("year_of_production", "Unknown Year")
            print(f"- {title} ({year})")
    except Exception as e:
        print(f"Error fetching SC wishlist: {e}")


# 3. Add to SensCritique Wishlist
def add_to_sc_wishlist(title, year):
    # Step 1: Search for the media by title and year
    search_query = gql("""
        query SearchMedia($keywords: String!) {
            searchResult(keywords: $keywords, limit: 5) {
                results {
                    products_list {
                        id
                        title
                        year_of_production
                    }
                }
            }
        }
    """)
    variables = {"keywords": title}
    search_results = sc_client.execute(search_query, variable_values=variables)
    media = None

    for result in search_results["searchResult"]["results"][0]["products_list"]:
        if result["year_of_production"] == year:
            media = result
            break

    if not media:
        print(f"Media '{title}' ({year}) not found in SensCritique.")
        return

    # Step 2: Add media to wishlist
    mutation = gql("""
        mutation AddToWishlist($productId: Int!) {
            productWish(productId: $productId)
        }
    """)

    try:
        sc_client.execute(mutation, variable_values={"productId": media["id"]})
        print(f"Successfully added '{media['title']}' ({media['year_of_production']}) to SensCritique wishlist.")
    except Exception as e:
        print(f"Error adding media to SensCritique wishlist: {e}")


# 4. Add to Plex Watchlist
def add_to_plex_watchlist(title: str, year: int):
    try:
        # Log into Plex account using the provided username and token
        account = MyPlexAccount(PLEX_USERNAME, token=PLEX_TOKEN)

        # Get the Plex server (we assume the first server, but you can choose a specific one)
        plex = account.resource("Plex Server").connect()

        # Search for the movie/series by title and year in the Movies library
        results = plex.library.section('Movies').search(title=title, year=year)

        if not results:
            print(f"No media found for '{title}' ({year}).")
            return

        # Assuming we want the first match
        item = results[0]
        print(f"Found '{item.title}' ({item.year}). Adding to the watchlist...")

        # Add the item to the watchlist
        item.addToWatchlist()

        print(f"Successfully added '{item.title}' ({item.year}) to the Plex watchlist.")

    except NotFound:
        print(f"The movie or series '{title}' ({year}) was not found in your Plex library.")
    except BadRequest as e:
        print(f"Error adding to Plex watchlist: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Main Function
def main():
    fetch_plex_watchlist()  # Fetch Plex Watchlist
    fetch_sc_wishlist()     # Fetch SC Wishlist

    title = "Amadeus"
    year = 1984


    add_to_plex_watchlist(title, year)  # Add to Plex Watchlist
    add_to_sc_wishlist(title, year)  # Add to SensCritique Wishlist


if __name__ == "__main__":
    main()
