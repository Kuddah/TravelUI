import requests

def get_amadeus_token(client_id, client_secret):
    token_url = 'https://test.api.amadeus.com/v1/security/oauth2/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code == 200:
        token = response.json().get('access_token')
        return token
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")



# Replace these with your own API key and secret
client_id = 'iApYXewA9W2JFPQggvjA46TsOSfV1fvb'
client_secret = 'ATEFOu6fmUGd79ki'

# Define the token endpoint and request headers
token_url = 'https://test.api.amadeus.com/v1/security/oauth2/token'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Prepare the POST request data
data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret
}

# Send the request and get the response
response = requests.post(token_url, headers=headers, data=data)

# Check if the request was successful
if response.status_code == 200:
    # Print the full output of the API call
    print(response.json())
else:
    print(f"Error: {response.status_code}, {response.text}")
