import urllib.request
import urllib.parse
import http.cookiejar
import re

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
url = 'http://127.0.0.1:5000/login'
html = op.open(url).read().decode('utf-8')
m = re.search(r'name="csrf_token" value="([^"]+)"', html)
if not m:
    raise SystemExit('no login csrf token')
token = m.group(1)
print('csrf login token', token)
data = {'email': 'admin@portal.com', 'password': 'Admin@123', 'csrf_token': token}
req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode('utf-8'), method='POST')
resp = op.open(req)
print('login status', resp.getcode(), resp.geturl())
html_new = op.open('http://127.0.0.1:5000/incidents/new').read().decode('utf-8')
m2 = re.search(r'name="csrf_token" value="([^"]+)"', html_new)
if not m2:
    raise SystemExit('no incident csrf token')
token2 = m2.group(1)
print('csrf incident token', token2)
data2 = {
    'title': 'Test Incident',
    'incident_type': 'Phishing',
    'description': 'Test incident details for diagnosis.',
    'incident_date': '2026-07-07',
    'csrf_token': token2
}
req2 = urllib.request.Request('http://127.0.0.1:5000/incidents/new', data=urllib.parse.urlencode(data2).encode('utf-8'), method='POST')
resp2 = op.open(req2)
print('post status', resp2.getcode(), resp2.geturl())
print(resp2.read().decode('utf-8')[:400])
