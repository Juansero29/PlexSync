import firebase_admin
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

SC_FIREBASE_API_KEY = os.getenv("SC_FIREBASE_API_KEY")


class SensCritiqueApp:

    # Firebase configuration (same as in the TypeScript code)
    firebaseConfig = {
        "apiKey": SC_FIREBASE_API_KEY,
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
