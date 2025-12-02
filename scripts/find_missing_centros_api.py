import requests

url = 'http://127.0.0.1:5000/api/usuarios'
resp = requests.get(url)
print('status', resp.status_code)
if resp.status_code != 200:
    print(resp.text)
    raise SystemExit(1)

data = resp.json()
usuarios = data.get('usuarios', [])
print('total usuarios:', len(usuarios))

empresa_val = 'FLEXIVEL-JGS'
licenca_val = 'Microsoft 365 Business Premium'

missing_rows = []
for u in usuarios:
    try:
        if (str(u.get('Empresa','')).strip()==empresa_val) and (str(u.get('Licenca') or u.get('licenca','')).strip()==licenca_val):
            centro = (u.get('Centro de Custo') or u.get('centro de custo') or '').strip()
            if centro == '' or centro.lower() in ['nan','none','nan.0']:
                missing_rows.append(u)
    except Exception:
        pass

print('Encontradas linhas sem Centro de Custo (contagem):', len(missing_rows))
for r in missing_rows[:50]:
    print({k: r.get(k) for k in ['Colaborador','Email','Empresa','Licenca','Centro de Custo','Data de Criação','Valor Total']})

# Save to file
if missing_rows:
    import csv
    keys = set()
    for r in missing_rows:
        keys.update(r.keys())
    keys = list(keys)
    with open('missing_centros_usuarios.json','w',encoding='utf-8') as f:
        import json
        json.dump(missing_rows, f, ensure_ascii=False, indent=2)
    print('Arquivo salvo: missing_centros_usuarios.json')
