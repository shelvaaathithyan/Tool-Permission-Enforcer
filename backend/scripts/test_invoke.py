import urllib.request, urllib.parse, json, urllib.error
data = urllib.parse.urlencode({'username': 'ravi.s@example.com', 'password': 'demo123'}).encode()
req = urllib.request.Request('http://localhost:8000/api/v1/auth/login', data=data)
token = json.loads(urllib.request.urlopen(req).read())['access_token']
invoke_req = urllib.request.Request('http://localhost:8000/api/v1/agent/invoke', data=json.dumps({'prompt': 'who works in XYXY Company?'}).encode(), headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
try:
    print(urllib.request.urlopen(invoke_req).read().decode())
except urllib.error.HTTPError as e:
    print(e.read().decode())
