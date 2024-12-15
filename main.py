import os
import asyncio
from dotenv import load_dotenv
from senscritique.senscritique_client import SensCritiqueClient
from plex.plex_client import PlexClient

# Load environment variables
load_dotenv()

SC_EMAIL = os.getenv("SC_EMAIL")
SC_PASSWORD = os.getenv("SC_PASSWORD")
SC_USER_ID=os.getenv("SC_USER_ID")

PLEX_TOKEN = os.getenv("PLEX_TOKEN")
PLEX_USERNAME = os.getenv("PLEX_USERNAME")


# Initialize the SensCritiqueClient
sc_client = SensCritiqueClient(SC_EMAIL, SC_PASSWORD, SC_USER_ID)

# Initialize Plex Client
plex_client = PlexClient(PLEX_USERNAME, PLEX_TOKEN)
    

async def main():
    await add_media_to_all_services_watchlist("Frozen", 2013, "movie")
    
if __name__ == "__main__":
    asyncio.run(main())  # This will run the async main function


async def add_media_to_all_services_watchlist(title, year, type):
    print(f"\nSearching for media from {year} on SensCritique...")
    media = await sc_client.fetch_media_id(title, year, universe= type)
    if media:
        await sc_client.add_media_to_wishlist(media["id"])

    await sc_client.fetch_user_wishes()
    
    media = plex_client.search_movie_in_plex(title, year, content_type=type)
    
    if media:
        plex_client.add_to_plex_watchlist(media)


async def print_both_wathclists():
    # Fetch and print the current wishlist from SensCritique
    print("Fetching current SensCritique Wishlist...")
    await sc_client.fetch_user_wishes()  # Make sure it's awaited
    
        # Fetch and print the current wishlist from SensCritique
    print("Fetching current Plex Watchlist...")
    plex_client.fetch_plex_watchlist()  # Make sure it's awaited