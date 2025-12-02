import requests
import csv
from io import StringIO

url = 'http://127.0.0.1:5000/api/rateio_contratos'
contracts = [{ 'empresa': 'FLEXIVEL-JGS', 'licenca': 'Microsoft 365 Business Premium' }]

resp = requests.post(url, json={'contracts': contracts})
print('status:', resp.status_code)
if resp.status_code != 200:
    print(resp.text)
    raise SystemExit(1)

content = resp.text
print('--- CSV preview ---')
print('\n'.join(content.splitlines()[:20]))

# parse semicolon-delimited
reader = csv.DictReader(StringIO(content), delimiter=';')
missing = []
rows = []
for r in reader:
    rows.append(r)
    centro = r.get('centro_custo','').strip()
    if centro == '':
        missing.append(r)

print('\nTotal linhas no CSV:', len(rows))
print('Linhas sem centro_custo:', len(missing))
if len(missing)>0:
    print('\nAmostra das linhas sem centro_custo:')
    for m in missing[:20]:
        print(m)
    # salvar em arquivo
    with open('rateio_export_latest_missing.csv','w',encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=reader.fieldnames, delimiter=';')
        w.writeheader()
        for m in missing:
            w.writerow(m)
    print('\nArquivo gerado: rateio_export_latest_missing.csv')
else:
    print('Nenhuma linha sem centro detectada no CSV retornado pelo servidor.')
