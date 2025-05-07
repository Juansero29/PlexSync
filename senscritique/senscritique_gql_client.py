import requests
from typing import Optional
from gql import Client
from gql.transport.requests import RequestsHTTPTransport
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
SC_EMAIL = os.getenv("SC_EMAIL")
SC_PASSWORD = os.getenv("SC_PASSWORD")

class SensCritiqueGqlClient(Client):
    def __init__(self, url: str, email: str, password: str):
        self.email = email
        self.password = password
        self.cookie_ref = None

        # Sign in immediately to obtain the cookieRef
        self.cookie_ref = self.sign_in_with_email_and_password()

        # Prepare headers for authenticated Apollo access
        headers = {
            "Authorization": self.cookie_ref,
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }

        transport = RequestsHTTPTransport(url=url, headers=headers)
        super().__init__(transport=transport)
        self.client = self  # Required for async raw_request

    @classmethod
    def build(cls, email: str, password: str) -> Optional['SensCritiqueGqlClient']:
        return cls("https://apollo.senscritique.com/", email, password)

    def sign_in_with_email_and_password(self) -> str:
        """
        Signs in via Apollo GraphQL mutation using email and password.
        Returns the cookieRef for future requests.
        """
        mutation = """
        mutation SignInWithEmailAndPasswordMutation($email: String!, $password: String!) {
          signInWithEmailAndPassword(email: $email, password: $password) {
            userCookie {
              cookieRef
              dateExpiration
              id
              userId
            }
          }
        }
        """

        variables = {
            "email": self.email,
            "password": self.password
        }

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://apollo.senscritique.com/",
            json={"query": mutation, "variables": variables},
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            cookie_ref = data["data"]["signInWithEmailAndPassword"]["userCookie"]["cookieRef"]
            print(f"Signed user {self.email} successfully with SensCritique API!")
            
            return cookie_ref
        else:
            raise Exception(f"Failed to sign in: {response.status_code} - {response.text}")

    async def request(self, document: str, variables: dict = None):
        return await self.raw_request(document, variables)

    async def raw_request(self, query, variables=None):
        """
        Executes a raw GraphQL request with Apollo cookieRef.
        """
        if not self.cookie_ref:
            raise ValueError("Not authenticated. No cookieRef available.")

        headers = {
            "Authorization": self.cookie_ref,
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }

        body = {
            "query": query,
            "variables": variables
        }

        response = requests.post(
            "https://apollo.senscritique.com/",
            json=body,
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"GraphQL request failed: {response.status_code} - {response.text}")
