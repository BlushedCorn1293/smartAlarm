import requests
import urllib.parse

# Authorization URL
# https://accounts.spotify.com/authorize?response_type=code&client_id=fa4ef692cad24fe39530ca8c98178070&redirect_uri=http://localhost:8888/callback&scope=user-modify-playback-state%20user-read-playback-state

# Replace with your actual values
CLIENT_ID = 'fa4ef692cad24fe39530ca8c98178070'
CLIENT_SECRET = 'dc5f925f960245a1a46b0d4ad1d70842'
REDIRECT_URI = 'http://localhost:8888/callback'
AUTHORIZATION_CODE = 'AQAAvyEPRtDDsM4EMO-c--pvdesIpzOVYKyHM8dAS44c6gRjXucgFjl63OnjXfb9Vd9s20IGuTEUuFtnMdYBiyiQK2ry9NOfzYXypvPJS8igSMTXXndNh9WqEAzGblI1eOP7E0n5tPSRFebliDl2Qn7pilLjT51X8ogAR_QYzR-B88QC_oaKNjFZgFA6f3IVyo5usX8IO88eFtAyczgTESXuLj7MnaEvIYasIwc1cfeBo5tRypnb0w'

# Spotify Token URL
TOKEN_URL = 'https://accounts.spotify.com/api/token'

# Prepare the POST data
data = {
    'grant_type': 'authorization_code',
    'code': AUTHORIZATION_CODE,
    'redirect_uri': REDIRECT_URI,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET
}

# Send the request to exchange the code for a token
response = requests.post(TOKEN_URL, data=data)

# If successful, you’ll receive a JSON with the access token
if response.status_code == 200:
    token_data = response.json()
    access_token = token_data['access_token']
    print(f"Access Token: {access_token}")
else:
    print(f"Error: {response.status_code}, {response.text}")

