import requests
from xml.etree import ElementTree

def get_user_rated_episodes(plex_ip, plex_port, plex_token):
    # Define the API endpoint for querying episodes with ratings
    url = f"http://{plex_ip}:{plex_port}/library/sections/1/all?type=4&userRating>=1&X-Plex-Token={plex_token}"
    
    # Send GET request
    response = requests.get(url)
    
    # Parse XML response
    if response.status_code == 200:
        tree = ElementTree.fromstring(response.content)
        
        # Find all episode elements (Video elements)
        episodes = tree.findall(".//Video")
        
        rated_episodes = []
        
        # Extract relevant details from each episode
        for episode in episodes:
            title = episode.get("title")
            year = episode.get("year")
            rating = episode.get("userRating")
            rating_key = episode.get("guid")
            season = episode.get("parentIndex")
            episode_index = episode.get("index")
            
            rated_episodes.append({
                'id': rating_key,
                'title': f"S{season.zfill(2)}E{episode_index.zfill(2)} - {title}",
                'year': year,
                'rating': rating
            })
        
        return rated_episodes
    
    else:
        print("Error fetching rated episodes:", response.status_code)
        return []

# Example usage
plex_ip = "127.0.0.1"  # Replace with your Plex server IP
plex_port = "32400"  # Replace with your Plex server port (default is 32400)
plex_token = "UUpCen37rycy8B2TM-Fs"  # Replace with your Plex authentication token
rated_episodes = get_user_rated_episodes(plex_ip, plex_port, plex_token)

for episode in rated_episodes:
    print(episode)
