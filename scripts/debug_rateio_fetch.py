import requests
url = 'http://127.0.0.1:5000/api/rateio_contratos'
contracts = [{ 'empresa': 'FLEXIVEL-JGS', 'licenca': 'Microsoft 365 Business Premium' }]
resp = requests.post(url, json={'contracts': contracts})
print('status', resp.status_code)
text = resp.text
lines = text.splitlines()
for i,l in enumerate(lines[:30]):
    parts = l.split(';')
    print(i, repr(l))
    for j,p in enumerate(parts):
        print('   ', j, repr(p))
    print()
print('\nTotal lines:', len(lines))
