import os
import asyncio
from dotenv import load_dotenv
from senscritique.senscritique_client import SensCritiqueClient
from plex.plex_client import PlexClient
import json

# Load environment variables
load_dotenv()



# Initialize the SensCritiqueClient
sc_client = SensCritiqueClient()

# Initialize Plex Client
plex_client = PlexClient()

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

def load_sync_data(file_path="sync_data.json"):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Return an empty list if the file doesn't exist

def update_sync_data(sync_data, plex_id, sc_id, title, year, media_type, status, file_path="sync_data.json"):
    item = {
        "plex_id": plex_id,
        "sc_id": sc_id,
        "title": title,
        "year": year,
        "type": media_type,
        "status": status
    }
    sync_data.append(item)
    
    # Write updated sync data back to the file
    with open(file_path, "w") as f:
        json.dump(sync_data, f, indent=4)

def find_sync_entry(sync_data, plex_id=None, sc_id=None):
    for entry in sync_data:
        if entry["plex_id"] == plex_id or entry["sc_id"] == sc_id:
            return entry
    return None

async def sync_watchlists():
    """Sync both Plex and SensCritique Watchlists."""
    print("Syncing Plex and SensCritique Watchlists...")

    # Fetch current watchlists
    plex_watchlist = plex_client.fetch_plex_watchlist()
    sc_wishlist = await sc_client.fetch_user_wishes()

    # Load sync data from the persistent file
    sync_data = load_sync_data()

    plex_titles = set()
    sc_titles = set()

    # Step 1: Add missing items (from Plex to SC and from SC to Plex)
    # Iterate over Plex Watchlist
    for plex_media in plex_watchlist:
        title = plex_media.title
        year = plex_media.year
        media_type = plex_media.type
        plex_id = plex_media.guid

        # Check if it's already in sync data
        sync_entry = find_sync_entry(sync_data, plex_id=plex_id)
        if not sync_entry:
            print(f"Adding '{title}' ({year}) to SensCritique wishlist...")
            media_id = await sc_client.fetch_media_id(title, year, universe=media_type)
            if media_id:
                await sc_client.add_media_to_wishlist(media_id)
                update_sync_data(sync_data, plex_id, media_id, title, year, media_type, "synced")

    # Iterate over SensCritique Wishlist and add missing items to Plex
    for sc_media in sc_wishlist:
        title = sc_media["title"]
        year = sc_media["release_date"].year
        media_type = sc_media["universe"]

        # Check if it's already in sync data
        sync_entry = find_sync_entry(sync_data, plex_id=None, sc_id=sc_media["id"])
        if not sync_entry:
            print(f"Adding '{title}' ({year}) to Plex watchlist...")
            plex_media = plex_client.search_media_in_plex(title, year, content_type=media_type)
            if plex_media:
                plex_client.add_to_plex_watchlist(plex_media)
                # Update the sync data after adding it to Plex
                update_sync_data(sync_data, plex_media.guid, sc_media["id"], title, year, media_type, "synced")

    # After adding, refresh the lists
    plex_watchlist = plex_client.fetch_plex_watchlist()
    sc_wishlist = await sc_client.fetch_user_wishes()
    
    # Step 2: Remove items no longer in the other list
    for entry in sync_data:
        title = entry["title"]
        year = entry["year"]
        media_type = entry["type"]
        status = entry["status"]

        # Check if the item is still in Plex or SC
        if status == "synced":
            # If it's missing from Plex, remove it from SensCritique (because it was removed from Plex)
            if not plex_watchlist or not any(p.title == title and p.year == year and p.type == media_type for p in plex_watchlist):
                print(f"Removing '{title}' ({year}) from SensCritique wishlist... (Plex removed it)")
                media_id = await sc_client.fetch_media_id(title, year, universe=media_type)
                if media_id:
                    await sc_client.remove_media_from_wishlist(media_id)
                # Update the sync status
                entry["status"] = "removed_from_sc"

            # If it's missing from SensCritique, remove it from Plex (because it was removed from SensCritique)
            elif not sc_wishlist or not any(s["title"] == title and s["release_date"].year == year and s["universe"] == media_type for s in sc_wishlist):
                print(f"Removing '{title}' ({year}) from Plex watchlist... (SensCritique removed it)")
                plex_media = plex_client.search_media_in_plex(title, year, content_type=media_type)
                if plex_media:
                    plex_client.remove_from_plex_watchlist(plex_media)
                # Update the sync status
                entry["status"] = "removed_from_plex"
            
                        # If it's missing from both, remove from the sync data
            if entry["status"] in ["removed_from_plex", "removed_from_sc"]:
                print(f"Removing '{title}' ({year}) from sync data... (both removed)")
                sync_data.remove(entry)

    # Save the updated sync data
    with open("sync_data.json", "w") as f:
        json.dump(sync_data, f, indent=4)

    print("Watchlist synchronization complete.")

async def print_plex_user_rated_content():
    rated_media = plex_client.get_user_rated_content()
    
    print(f"All media rated in Plex ({len(rated_media)} items):")
    for media in rated_media:
        print(f"[{media['type']}] {media['title']} ({media['year']}): {media['rating']} [{media['id']}]")
        
async def print_sens_critique_user_rated_content():
    rated_media = await sc_client.get_user_rated_media()
    print(f"All media rated in SensCritique ({len(rated_media)} items):")
    for media in rated_media:
        print(f"[{media['type']}] {media['title']} ({media['year']}): {media['rating']} [{media['id']}]")

async def main():

    
    # await sync_watchlists()
    # await sc_client.rate_media_with_id(85619210, 6)
    media = plex_client.search_media_in_plex("herbie", 2010, "movie")
    plex_client.rate_media_with_id(media, 7)

if __name__ == "__main__":
    asyncio.run(main())  # This will run the async main function
