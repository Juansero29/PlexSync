import firebase_admin

class SensCritiqueApp:

    # SensCritique GraphQL API URL
    senscritiqueGQLApi = "https://gql.senscritique.com/graphql"

    # Firebase configuration (same as in the TypeScript code)
    firebaseConfig = {
        "apiKey": 'AIzaSyAHxGE6otUcjogt6EXNzXrAZJr99WZ1MdI',
        "authDomain": 'fir-sc-ea332.firebaseapp.com',
        "databaseURL": 'https://fir-sc-ea332.firebaseio.com',
        "projectId": 'fir-sc-ea332',
        "storageBucket": 'fir-sc-ea332.appspot.com',
    }

    # Firebase app initialization (using the default app, no need for a JSON file)
    firebaseApp = firebase_admin.initialize_app()

    def __init__(self):
        """Initialize the SensCritiqueApp."""
        pass  # No need for additional logic here since everything is static
