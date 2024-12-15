import os
from dotenv import load_dotenv
from senscritique.senscritique_client import SensCritiqueClient

# Load environment variables
load_dotenv()

SC_EMAIL = os.getenv("SC_EMAIL")
SC_PASSWORD = os.getenv("SC_PASSWORD")

def main():
    # Initialize the SensCritiqueClient
    sc_client = SensCritiqueClient(SC_EMAIL, SC_PASSWORD)
    
    # Fetch and print the current wishlist from SensCritique
    print("Fetching current SensCritique Wishlist...")
    sc_client.fetch_user_wishes(limit=30)
    
    # Search for a movie from 2013 (for example, "Frozen")
    title = "Frozen"
    year = 2013
    universe = "movie"  # Or "tvshow"
    
    print(f"\nSearching for media from {year} on SensCritique...")
    media_id = sc_client.fetch_media_id(title, year, universe)
    
    if media_id:
        print(f"Found media ID: {media_id}")
        print(f"Adding media '{title}' ({year}) to the wishlist...")
        
        # Add the media to SensCritique wishlist
        sc_client.add_media_to_wishlist(media_id)
    else:
        print(f"Media '{title}' ({year}) not found in SensCritique.")

    # Fetch and print the updated wishlist from SensCritique
    print("\nFetching updated SensCritique Wishlist...")
    sc_client.fetch_user_wishes()
    
    
    
if __name__ == "__main__":
    main()
