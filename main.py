import stealth_requests as requests

s = requests.StealthSession()

x = s.get('https://www.pokerstarsmi.com')
print(x.status_code)

# Login
url = 'https://www.pokerstarsmi.com/api/v1-preview/auth/session'
myobj = {'installId': '102133820445328422', 'userId': 'YOUR_USERNAME', 'password': 'YOUR_PASSWORD'}
x = s.post(url, json=myobj)
print(x.status_code)
print(x.content)
print(x.cookies)

# Export 7 days of hand history
url = 'https://www.pokerstarsmi.com/api/v1-preview/account/history/client-history'
myobj = {'locale': 0, 'requestType': 1, 'param': 604800}
x = s.post(url, json=myobj)
print(x.status_code)
print(x.content)

# Logout
url = 'https://www.pokerstarsmi.com/api/v1-preview/auth/session'
x = s.delete(url)
print(x.status_code)
print(x.content)
