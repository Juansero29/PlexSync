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

async def add_all_plex_watchlist_to_sc():
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

async def add_all_scs_wishlist_to_plex():
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
        plex_media = plex_client.search_media_in_plex(title, year, content_type=universe)

        if plex_media:
            print(f"Adding '{title}' ({year}) to Plex watchlist...")
            plex_client.add_to_plex_watchlist(plex_media)
        else:
            print(f"'{title}' ({year}) not found in Plex.")
    
    print("Finished adding movies/series to Plex watchlist.")

async def remove_plex_watchlist_removed_items_in_sc():
    """Sync items removed from Plex Watchlist to SensCritique Wishlist."""
    print("Fetching Plex Watchlist...")
    plex_watchlist = plex_client.fetch_plex_watchlist()

    # Fetch current SensCritique wishlist
    print("Fetching SensCritique Wishlist...")
    sc_wishlist = await sc_client.fetch_user_wishes(limit=30)  # Adjust the limit as needed
    
    # Create a list of titles from both lists to compare
    plex_titles = [(plex_media.title, plex_media.year, plex_media.type) for plex_media in plex_watchlist]
    sc_titles = [(media['title'], media['release_date'].year, media['universe']) for media in sc_wishlist]

    # Find items that are in Plex but not in SC wishlist
    items_to_remove_from_sc = [plex_media for plex_media in plex_titles if (plex_media[0], plex_media[1], plex_media[2]) not in sc_titles]

    if items_to_remove_from_sc:
        print(f"Found {len(items_to_remove_from_sc)} items to remove from SensCritique Wishlist.")
        for plex_media in items_to_remove_from_sc:
            # Search the media on SensCritique by title, year, and type (universe)
            media_id = await sc_client.fetch_media_id(plex_media[0], plex_media[1], universe=plex_media[2])
            if media_id:
                print(f"Removing {plex_media[0]} ({plex_media[1]}) from SensCritique Wishlist...")
                await sc_client.remove_media_from_wishlist(media_id)
    else:
        print("No items to remove from SensCritique Wishlist.")

async def remove_sc_wishlist_removed_items_in_plex():
    """Sync items removed from SensCritique Wishlist to Plex Watchlist."""
    print("Fetching SensCritique Wishlist...")
    sc_wishlist = await sc_client.fetch_user_wishes(limit=30)  # Adjust the limit as needed

    # Fetch current Plex watchlist
    print("Fetching Plex Watchlist...")
    plex_watchlist = plex_client.fetch_plex_watchlist()

    # Create a list of titles from both lists to compare
    plex_titles = [(plex_media.title, plex_media.year, plex_media.type) for plex_media in plex_watchlist]
    sc_titles = [(media['title'], media['release_date'].year, media['universe']) for media in sc_wishlist]

    # Find items that are in SC wishlist but not in Plex's watchlist
    items_to_remove_from_plex = [sc_media for sc_media in sc_titles if (sc_media[0], sc_media[1], sc_media[2]) not in plex_titles]

    if items_to_remove_from_plex:
        print(f"Found {len(items_to_remove_from_plex)} items to remove from Plex Watchlist.")
        for sc_media in items_to_remove_from_plex:
            # Search the media on Plex by title, year, and type (universe)
            plex_media = plex_client.search_media_in_plex(sc_media[0], sc_media[1], content_type=sc_media[2])
            if plex_media:
                print(f"Removing {sc_media[0]} ({sc_media[1]}) from Plex Watchlist...")
                plex_client.remove_from_plex_watchlist(plex_media)
    else:
        print("No items to remove from Plex Watchlist.")

async def sync_watchlists():
    """Sync both Plex and SC watchlists."""
    print("Syncing Plex and SensCritique Watchlists...")

    # Fetch current watchlists
    plex_watchlist = plex_client.fetch_plex_watchlist()
    sc_wishlist = await sc_client.fetch_user_wishes()

    # Prepare a set of titles for comparison
    plex_titles = set()
    sc_titles = set()

    if plex_watchlist:
        plex_titles = set((plex_media.title, plex_media.year, plex_media.type) for plex_media in plex_watchlist)

    if sc_wishlist:
        sc_titles = set((media["title"], media["release_date"].year, media["universe"]) for media in sc_wishlist)

    # Step 1: Add missing items (from Plex to SC and from SC to Plex)

    # Items in Plex but not in SC (i.e., add these to SC)
    items_to_add_to_sc = plex_titles - sc_titles
    for title, year, universe in items_to_add_to_sc:
        print(f"Adding '{title}' ({year}) to SensCritique wishlist...")
        media_id = await sc_client.fetch_media_id(title, year, universe)
        if media_id:
            await sc_client.add_media_to_wishlist(media_id)

    # Items in SC but not in Plex (i.e., add these to Plex)
    items_to_add_to_plex = sc_titles - plex_titles
    for title, year, universe in items_to_add_to_plex:
        print(f"Adding '{title}' ({year}) to Plex watchlist...")
        plex_media = plex_client.search_media_in_plex(title, year, content_type=universe)
        if plex_media:
            plex_client.add_to_plex_watchlist(plex_media)

    # Step 2: Remove items no longer in the other list

    # Items that are in both Plex and SC but missing from the other list
    items_to_remove_from_plex = plex_titles - sc_titles
    for title, year, universe in items_to_remove_from_plex:
        print(f"Removing '{title}' ({year}) from Plex watchlist...")
        plex_media = plex_client.search_media_in_plex(title, year, content_type=universe)
        if plex_media:
            plex_client.remove_from_plex_watchlist(plex_media)

    # Items that are in both SC and Plex but missing from the other list
    items_to_remove_from_sc = sc_titles - plex_titles
    for title, year, universe in items_to_remove_from_sc:
        print(f"Removing '{title}' ({year}) from SensCritique wishlist...")
        media_id = await sc_client.fetch_media_id(title, year, universe)
        if media_id:
            await sc_client.remove_media_from_wishlist(media_id)

    print("Watchlist synchronization complete.")


async def add_media_to_all_services_watchlist(title, year, type):
    try:
        print(f"\nSearching for media from {year} on SensCritique...")
        media_id = await sc_client.fetch_media_id(title, year, universe=type)
        if media_id:
            await sc_client.add_media_to_wishlist(media_id)

        # Fetch updated wishlist after adding media
        await sc_client.fetch_user_wishes()

        print(f"\nSearching for media from {year} on Plex...")
        plex_media = plex_client.search_media_in_plex(title, year, content_type=type)

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

    

async def main():
    # await search_movie_in_sc_diary("Frozen", 2013, "movie")
    await sync_watchlists()

if __name__ == "__main__":
    asyncio.run(main())  # This will run the async main function
