import json
import requests
from typing import Optional
from gql import Client, gql
import base64
import time
from gql.transport.requests import RequestsHTTPTransport
from .senscritiqueapp import SensCritiqueApp

import json
import requests
from typing import Optional
from gql import Client, gql
import base64
import time
from gql.transport.requests import RequestsHTTPTransport
from .senscritiqueapp import SensCritiqueApp


import os
from dotenv import load_dotenv
from plex.plex_client import PlexClient
import json

# Load environment variables
load_dotenv()

SC_EMAIL = os.getenv("SC_EMAIL")
SC_PASSWORD = os.getenv("SC_PASSWORD")
SC_USER_ID = os.getenv("SC_USER_ID")
SC_USERNAME = os.getenv("SC_USERNAME")

class SensCritiqueGqlClient(Client):
    def __init__(self, url: str, user_credentials: dict):
        self.user_credentials = user_credentials
        self.id_token = None
        self.apollo_cookie_ref = None
        # Get the Firebase ID Token
        token = self.get_id_token()

        # Define headers with Authorization and User-Agent
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Initialize the parent Client class with the necessary transport
        transport = RequestsHTTPTransport(url=url, headers=headers)
        super().__init__(transport=transport)
        
        # Ensure the `client` attribute is initialized after calling super
        self.client = self

    @classmethod
    def build(cls, email: str, password: str, use_apollo=False) -> 'SensCritiqueGqlClient':
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
            
            print("Logged into firebase successfully!")
            
                   # Determine the appropriate API endpoint
            api_url = "https://apollo.senscritique.com/" if use_apollo else "https://gql.senscritique.com/graphql"
        
            return cls(api_url, user_credentials)
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
        
    async def request(self, document: str, variables: dict = None, use_apollo=False, is_signin=False):
        """
        Executes a GraphQL query using the standard request method.
        """
        return await self.raw_request(document, variables, use_apollo, is_signin)

    async def raw_request(self, query, variables=None, use_apollo=False, is_signin=False):
        """Execute a raw GraphQL request with the provided query and variables."""
        if not self.client:
            raise ValueError("GraphQL client is not initialized.")
        
        # Determine the appropriate API endpoint
        api_url = "https://apollo.senscritique.com/" if use_apollo else "https://gql.senscritique.com/graphql"
        
        if use_apollo and not self.apollo_cookie_ref and not is_signin:
            await self.sign_in_with_email_and_password()
        
        # Get the Firebase ID Token
        token = self.apollo_cookie_ref if use_apollo else self.get_id_token()

        if not use_apollo and (not token or len(token.split('.')) != 3):
            raise ValueError("Invalid Firebase ID token. Make sure you're passing the complete JWT.")



        # Prepare the request payload with the Authorization header and User-Agent
        headers = {
            "Authorization": token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json"
        }
        
        body = {
            "query": query,
            "variables": variables
        }
        
        # Send the request with headers and query/variables
        response = requests.post(api_url, json=body, headers=headers)

        # Log the response for debugging purposes
        # print(f"Response body: {response.text}")

        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(f"Request failed with status {response.status_code}: {response.text}")
        
    async def sign_in_with_email_and_password(self):
        """Sign in using email and password, store cookieRef for future requests."""
        
        # Define the GraphQL mutation for signing in
        query = """
        mutation SignInWithEmailAndPasswordMutation($email: String!, $password: String!) {
          signInWithEmailAndPassword(email: $email, password: $password) {
            me {
              email
              firstName
              id
              lastName
              name
              username
              validEmail
              __typename
            }
            userCookie {
              applicationId
              cookieRef
              dateExpiration
              id
              userId
              __typename
            }
            __typename
          }
        }
        """

        variables = {
            "email": SC_EMAIL,
            "password": SC_PASSWORD
        }

        # Send the request using the Apollo client
        response = await self.client.request(query, variables, use_apollo=True, is_signin=True)

        # Check the response
        if "data" in response and "signInWithEmailAndPassword" in response["data"]:
            user_cookie = response["data"]["signInWithEmailAndPassword"]["userCookie"]
            
            # If the cookieRef is returned, store it
            if user_cookie and "cookieRef" in user_cookie:
                self.apollo_cookie_ref = user_cookie["cookieRef"]
            else:
                print("Failed to retrieve the cookieRef from the response.")
                return None
        else:
            print("Sign-in failed to SensCritique-Apollo. Please check your credentials.")
            return None

        # Return the cookieRef for future use
        return self.apollo_cookie_ref

