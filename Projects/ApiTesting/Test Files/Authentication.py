import requests

R=requests.get('https://stackexchange.com/oauth', auth=('zeuz.framework@gmail.com', 'asdfQWER1234'))


print R.status_code
print R.headers
print R.encoding

print R.headers['X-Request-Guid']








