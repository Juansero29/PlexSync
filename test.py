import requests
import json

# SensCritique GraphQL API URL
url = 'https://gql.senscritique.com/graphql'

# GraphQL Query
query = """
    query UserWishes($id: Int!, $limit: Int) {
        user(id: $id) {
            id
            wishes(limit: $limit) {
                title
                year_of_production
            }
        }
    }
"""

# Variables for the query
variables = {"id": 724296, "limit": 30}

# Firebase ID Token (replace with your actual token)
id_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjFhYWMyNzEwOTkwNDljMGRmYzA1OGUwNjEyZjA4ZDA2YzMwYTA0MTUiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiSnVhbnNlcm8yOSIsInNjSWQiOjcyNDI5NiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL2Zpci1zYy1lYTMzMiIsImF1ZCI6ImZpci1zYy1lYTMzMiIsImF1dGhfdGltZSI6MTczNDI2Njg1MywidXNlcl9pZCI6IjcyNDI5NiIsInN1YiI6IjcyNDI5NiIsImlhdCI6MTczNDI2Njg1MywiZXhwIjoxNzM0MjcwNDUzLCJlbWFpbCI6Imp1YW5zZXJvMjlAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7ImZhY2Vib29rLmNvbSI6WyIxMDE1ODc5MjY4MjQwODA1NyJdLCJlbWFpbCI6WyJqdWFuc2VybzI5QGdtYWlsLmNvbSJdfSwic2lnbl9pbl9wcm92aWRlciI6InBhc3N3b3JkIn19.FfKqG79JhDhkHqQDYQU0G9qCn2EldWh5d52lKvkjaNIIVFx34-sakGD5FgXwM4KI_FXbmlzlPFwLSIXkKdg33TTI91WsSTpvaeH9P4otc5bCsQMOntXEa99NP6HnmN1MGm3nQ-ANyq_E-W0nY_aZAErSQ5tv1KLY_c8NTyOKG9sufIYljLle7VssBujG29A2iEKf_mZdk5wHohHwcx2r5LKSyc740_OmyzzeqgEuE27c2Fn38fWC2t7J_TyGLUP8vkQttmhUBnPKfSRgHBPPAjEzTVJrwD6ok_69SLFwp2U7oCIrP_ZzUGnYes8oqDFihZq2bh3zx_mUNuC_K_fAuQ'

# Headers to be included in the request
headers = {
    "Authorization": f"Bearer {id_token}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Content-Type": "application/json"
}

# Payload for the request
payload = {
    "query": query,
    "variables": variables
}

# Send the request with headers and query/variables
response = requests.post(url, json=payload, headers=headers)

# Print the response content
print(response.status_code)
print(response.json())  # This will print the response JSON if successful
