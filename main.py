import os
import asyncio
from dotenv import load_dotenv
from senscritique.senscritique_client import SensCritiqueClient
from plex.plex_client import PlexClient

# Load environment variables
load_dotenv()

SC_EMAIL = os.getenv("SC_EMAIL")
SC_PASSWORD = os.getenv("SC_PASSWORD")
SC_USER_ID = os.getenv("SC_USER_ID")

PLEX_TOKEN = os.getenv("PLEX_TOKEN")
PLEX_USERNAME = os.getenv("PLEX_USERNAME")


# Initialize the SensCritiqueClient
sc_client = SensCritiqueClient(SC_EMAIL, SC_PASSWORD, SC_USER_ID)

# Initialize Plex Client
plex_client = PlexClient(PLEX_USERNAME, PLEX_TOKEN)

async def sync_plex_watchlist_to_sc():
    """Sync all items in Plex Watchlist to SensCritique's wishlist."""
    
    print("Fetching Plex Watchlist...")
    plex_watchlist = plex_client.fetch_plex_watchlist()

    if plex_watchlist:
        for plex_media in plex_watchlist:
            title = plex_media.title
            year = plex_media.year
            content_type = plex_media.type  # This will be either 'movie' or 'tvshow'

            print(f"\nSearching for {title} ({year}) on SensCritique...")

            # Fetch the media ID from SensCritique
            media_id = await sc_client.fetch_media_id(title, year, universe=content_type)

            if media_id:
                print(f"Adding {title} ({year}) to SensCritique wishlist...")
                await sc_client.add_media_to_wishlist(media_id)
            else:
                print(f"Could not find {title} ({year}) on SensCritique.")
    else:
        print("No items found in Plex Watchlist.")

async def sync_scs_wishlist_to_plex():
    """Sync all movies/series in SensCritique's wishlist into Plex's watchlist."""
    
    # Fetch the user's wishlist from SensCritique and store it in a variable
    print("Fetching user wishlist from SensCritique...")
    sc_wishlist = await sc_client.fetch_user_wishes(limit=30)  # Fetch the first 30 items
    
    if not sc_wishlist:
        print("No wishlist found in SensCritique.")
        return
    
    print(f"Found {len(sc_wishlist)} items in SensCritique wishlist.")
    
    # Iterate through each media in the wishlist
    for media in sc_wishlist:
        title = media["title"]
        year = media["release_date"].year
        universe = media["universe"]

        print(f"Searching for '{title}' ({year}) in Plex...")

        # Search for the movie/series in Plex
        plex_media = plex_client.search_movie_in_plex(title, year, content_type=universe)

        if plex_media:
            print(f"Adding '{title}' ({year}) to Plex watchlist...")
            plex_client.add_to_plex_watchlist(plex_media)
        else:
            print(f"'{title}' ({year}) not found in Plex.")
    
    print("Finished adding movies/series to Plex watchlist.")

async def add_media_to_all_services_watchlist(title, year, type):
    try:
        print(f"\nSearching for media from {year} on SensCritique...")
        media_id = await sc_client.fetch_media_id(title, year, universe=type)
        if media_id:
            await sc_client.add_media_to_wishlist(media_id)

        # Fetch updated wishlist after adding media
        await sc_client.fetch_user_wishes()

        print(f"\nSearching for media from {year} on Plex...")
        plex_media = plex_client.search_movie_in_plex(title, year, content_type=type)

        if plex_media:
            plex_client.add_to_plex_watchlist(plex_media)
        else:
            print(f"Media '{title}' ({year}) not found in Plex.")
    except Exception as e:
        print(f"Error adding media to all services watchlist: {e}")

async def print_both_watchlists():
    try:
        # Fetch and print the current wishlist from SensCritique
        print("Fetching current SensCritique Wishlist...")
        await sc_client.fetch_user_wishes()

        # Fetch and print the current watchlist from Plex
        print("Fetching current Plex Watchlist...")
        plex_client.fetch_plex_watchlist()
    except Exception as e:
        print(f"Error printing watchlists: {e}")

async def search_movie_in_sc_diary(title, year, type):
    media_id = await sc_client.fetch_media_id(title, year, universe=type)
    
    media = await sc_client.fetch_from_user_collections(media_id)
    
    print("Date Added To Wish List:", media["dateLastUpdate"])
    
    

async def main():
    await search_movie_in_sc_diary("Frozen", 2013, "movie")

if __name__ == "__main__":
    asyncio.run(main())  # This will run the async main function
