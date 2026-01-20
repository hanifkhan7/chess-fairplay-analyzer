import requests

headers1 = {
    'Accept': 'application/x-ndjson',
    'User-Agent': 'Chess-Fairplay-Analyzer/3.0'
}

headers2 = {
    'Accept': 'application/x-ndjson'
}

url = 'https://lichess.org/api/games/user/Pap-G'
params = {
    'max': 5,
    'sort': 'dateDesc'
}

print("Test 1: With User-Agent")
try:
    response = requests.get(url, headers=headers1, params=params, timeout=5)
    print(f'✓ Status: {response.status_code}')
except Exception as e:
    print(f'✗ Error: {str(e)[:80]}')

print("\nTest 2: Without User-Agent")
try:
    response = requests.get(url, headers=headers2, params=params, timeout=5)
    print(f'✓ Status: {response.status_code}')
except Exception as e:
    print(f'✗ Error: {str(e)[:80]}')

print("\nTest 3: Minimal headers")
try:
    response = requests.get(url, headers={'Accept': 'application/x-ndjson'}, params=params, timeout=5)
    print(f'✓ Status: {response.status_code}')
    print(f'  Got {len(response.text)} bytes')
except Exception as e:
    print(f'✗ Error: {str(e)[:80]}')
