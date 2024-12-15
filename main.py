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

async def main():
    # Initialize the SensCritiqueClient
    sc_client = SensCritiqueClient(SC_EMAIL, SC_PASSWORD, SC_USER_ID)
    plex_client = PlexClient(PLEX_USERNAME, PLEX_TOKEN)
    
    # Fetch and print the current wishlist from SensCritique
    print("Fetching current SensCritique Wishlist...")
    await sc_client.fetch_user_wishes()  # Make sure it's awaited
    
        # Fetch and print the current wishlist from SensCritique
    print("Fetching current Plex Watchlist...")
    plex_client.fetch_plex_watchlist()  # Make sure it's awaited
    
    # Search for a movie from 2013 (for example, "Frozen")
    title = "Frozen"
    year = 2013
    universe = "movie"  # Or "tvshow"
    
    print(f"\nSearching for media from {year} on SensCritique...")
    media_id = await sc_client.fetch_media_id(title, year, universe)  # Make sure it's awaited
    
    if media_id:
        print(f"Found media ID: {media_id}")
        # print(f"Adding media '{title}' ({year}) to the wishlist...")
        
        # # Add the media to SensCritique wishlist
        await sc_client.add_media_to_wishlist(media_id)  # Make sure it's awaited
    else:
        print(f"Media '{title}' ({year}) not found in SensCritique.")

    # # Fetch and print the updated wishlist from SensCritique
    # print("\nFetching updated SensCritique Wishlist...")
    await sc_client.fetch_user_wishes()  # Make sure it's awaited

if __name__ == "__main__":
    asyncio.run(main())  # This will run the async main function
