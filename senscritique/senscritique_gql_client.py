import json
import requests
from typing import Optional
from gql import Client, gql
import base64
import time
from gql.transport.requests import RequestsHTTPTransport
from .senscritiqueapp import SensCritiqueApp


class SensCritiqueGqlClient(Client):
    def __init__(self, url: str, user_credentials: dict):
        self.user_credentials = user_credentials
        self.id_token = None
        
        # Initialize the parent Client class (this will set up the internal `client` attribute)
        transport = RequestsHTTPTransport(url=url)
        super().__init__(transport=transport)
        
        # Ensure that the `client` attribute is initialized after calling super
        self.client = self

    @classmethod
    def build(cls, email: str, password: str) -> 'SensCritiqueGqlClient':
        """
        Logs in using Firebase authentication via REST API and returns a SensCritiqueGqlClient instance.
        """
        # Firebase Auth REST API endpoint for email/password sign-in
        firebase_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={SensCritiqueApp.firebaseConfig['apiKey']}"
        
        # Payload for Firebase sign-in
        payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }

        # Make the request to Firebase Auth REST API
        response = requests.post(firebase_url, json=payload)

        if response.status_code == 200:
            # Parse the user credentials from the Firebase response
            user_credentials = response.json()
            return cls(SensCritiqueApp.senscritiqueGQLApi, user_credentials)
        else:
            print(f"Error signing in: {response.text}")
            return None

    @classmethod
    def build_from_state(cls, user_credentials: dict) -> 'SensCritiqueGqlClient':
        """
        Builds the client from an existing user session.
        """
        return cls(SensCritiqueApp.senscritiqueGQLApi, user_credentials)

    def get_id_token(self) -> Optional[str]:
        """
        Retrieves the Firebase ID Token.
        """
        if self.id_token:
            # Token logic for expiration checks
            claims = json.loads(base64.b64decode(self.id_token.split('.')[1]).decode())
            expiration = claims['exp'] * 1000
            if expiration > int(time.time() * 1000):  # token is still valid
                return self.id_token

        if self.user_credentials:
            # Request a new token if expired or not available
            id_token = self.user_credentials.get('idToken')
            self.id_token = id_token
            return id_token
        else:
            raise Exception("User credentials are missing")

    def request(self, document: str, variables: dict = None, request_headers: Optional[dict] = None):
        """
        Executes a GraphQL query using the standard request method.
        """
        return self.raw_request(document, variables, request_headers)
    
    def raw_request(self, query, variables=None):
        """Execute a raw GraphQL request with the provided query and variables."""
        if not self.client:
            raise ValueError("GraphQL client is not initialized.")
        return self.client.execute(gql(query), variable_values=variables)