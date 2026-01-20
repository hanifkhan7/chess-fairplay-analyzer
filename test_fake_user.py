import requests
url = 'https://api.chess.com/pub/player/xyzabc123notarealuser'
response = requests.get(url, timeout=5)
print(f'Status: {response.status_code}')
if response.status_code == 200:
    print(f'✓ User exists')
elif response.status_code == 403:
    print(f'✓ User exists but private')
elif response.status_code == 404:
    print(f'✗ User not found')
else:
    print(f'? Unknown status')
