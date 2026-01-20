import requests

# Test Quantum-Chesss on Chess.com
print('Testing Quantum-Chesss on Chess.com:')
url = 'https://api.chess.com/pub/player/quantum-chesss'
print(f'URL: {url}')
response = requests.get(url, timeout=5)
print(f'Status: {response.status_code}')
if response.status_code == 200:
    print('✓ Found on Chess.com')
    print(response.json())
else:
    print('✗ Not found')

print('\n' + '='*60 + '\n')

# Test Pap-G on Lichess
print('Testing Pap-G on Lichess:')
url = 'https://lichess.org/api/user/pap-g'
headers = {'Accept': 'application/json'}
response = requests.get(url, headers=headers, timeout=5)
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'✓ Found on Lichess')
    print(f'  Username: {data.get("username", "N/A")}')
    print(f'  Games Count: {data.get("count", {}).get("all", 0)}')
    print(f'  Bullet: {data.get("count", {}).get("bullet", 0)}')
    print(f'  Blitz: {data.get("count", {}).get("blitz", 0)}')
    print(f'  Rapid: {data.get("count", {}).get("rapid", 0)}')
    print(f'  Classical: {data.get("count", {}).get("classical", 0)}')
else:
    print('✗ Not found')
    print(f'Response: {response.text[:200]}')
