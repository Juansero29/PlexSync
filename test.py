import requests
import json
from datetime import datetime

def fetch_user_collection(username, limit=5000):
    url = "https://apollo.senscritique.com/"
    
    query = """
    query UserDiary($isDiary: Boolean, $limit: Int, $offset: Int, $universe: String, $username: String!, $yearDateDone: Int) {
        user(username: $username) {
            collection(isDiary: $isDiary, limit: $limit, offset: $offset, universe: $universe, yearDateDone: $yearDateDone) {
                products {
                    id
                    universe
                    category
                    title
                    originalTitle
                    alternativeTitles
                    yearOfProduction
                    url
                    otherUserInfos(username: $username) {
                        dateDone
                        rating
                    }
                }
            }
        }
    }
    """
    
    variables = {
        "isDiary": True,
        "limit": limit,
        "universe": None,
        "username": username,
        "yearDateDone": None
    }

    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }

    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        products = data.get('data', {}).get('user', {}).get('collection', {}).get('products', [])

        # Transforming dateDone to a readable format
        for product in products:
            user_info = product.get('otherUserInfos', [{}])[0]
            if 'dateDone' in user_info:
                try:
                    # Handle the date transformation
                    user_info['dateDone'] = datetime.strptime(user_info['dateDone'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%dT%H:%M:%S %Z")
                except ValueError:
                    # If there's an issue parsing the date, we keep it as is
                    pass

        return products
    else:
        print("Error fetching data:", response.text)
        return []

# Example usage
username = "juansero29"
products = fetch_user_collection(username)

# Saving the result to a JSON file
with open(f"backup_senscritique_{datetime.now().strftime('%Y-%m-%d')}.json", "w") as file:
    json.dump(products, file, indent=2)

print(f"Data saved to backup_senscritique_{datetime.now().strftime('%Y-%m-%d')}.json")
