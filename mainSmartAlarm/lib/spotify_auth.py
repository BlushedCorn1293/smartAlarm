import urequests
import ubinascii
import json
import time
import os


class SpotifyAuth:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_url = 'https://accounts.spotify.com/api/token'
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = 0
        self.token_file = 'spotify_tokens.json'
        
        # Try to load existing tokens
        self.load_tokens()

    def load_tokens(self):
        """Load tokens from file if they exist"""
        try:
            if self.token_file in os.listdir():
                with open(self.token_file, 'r') as f:
                    token_data = json.loads(f.read())
                    self.access_token = token_data.get('access_token')
                    self.refresh_token = token_data.get('refresh_token')
                    self.token_expiry = token_data.get('expiry', 0)
        except Exception as e:
            print(f"Error loading tokens: {e}")

    def save_tokens(self):
        """Save tokens to file"""
        token_data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expiry': self.token_expiry
        }
        with open(self.token_file, 'w') as f:
            f.write(json.dumps(token_data))

    def get_auth_header(self):
        """Create the authorization header"""
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_base64 = ubinascii.b2a_base64(auth_bytes).decode('ascii').strip()
        return {'Authorization': f'Basic {auth_base64}'}

    def get_initial_tokens(self, auth_code):
        """Exchange authorization code for tokens"""
        headers = self.get_auth_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        body = (
            f"grant_type=authorization_code"
            f"&code={auth_code}"
            f"&redirect_uri={self.redirect_uri}"
        )
        
        try:
            response = urequests.post(self.token_url, headers=headers, data=body)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.refresh_token = token_data['refresh_token']
                self.token_expiry = time.time() + token_data['expires_in']
                self.save_tokens()
                return True
            else:
                print(f"Error getting tokens: {response.text}")
                return False
        except Exception as e:
            print(f"Error during token exchange: {e}")
            return False
        finally:
            if 'response' in locals():
                response.close()

    def refresh_access_token(self):
        """Refresh the access token using the refresh token"""
        if not self.refresh_token:
            print("No refresh token available")
            return False

        headers = self.get_auth_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        body = (
            f"grant_type=refresh_token"
            f"&refresh_token={self.refresh_token}"
        )
        
        try:
            response = urequests.post(self.token_url, headers=headers, data=body)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.token_expiry = time.time() + token_data['expires_in']
                # Some responses also include a new refresh token
                if 'refresh_token' in token_data:
                    self.refresh_token = token_data['refresh_token']
                self.save_tokens()
                return True
            else:
                print(f"Error refreshing token: {response.text}")
                return False
        except Exception as e:
            print(f"Error during token refresh: {e}")
            return False
        finally:
            response.close()

    def get_valid_access_token(self):
        """Get a valid access token, refreshing if necessary"""
        # If we have no tokens, we need initial authorization
        if not self.access_token or not self.refresh_token:
            print("No tokens available. Initial authorization required.")
            return None
        
        # If token is expired or will expire in next 60 seconds, refresh it
        if time.time() + 60 >= self.token_expiry:
            if not self.refresh_access_token():
                print("Failed to refresh token")
                return None
        return self.access_token
    
    