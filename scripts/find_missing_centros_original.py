import pandas as pd

EXCEL_FILE = 'LICENCIAMENTO MICROSOFT (1).xlsx'
print('Lendo', EXCEL_FILE)
df = pd.read_excel(EXCEL_FILE, sheet_name='Planilha1')
empresa_val = 'FLEXIVEL-JGS'
licenca_val = 'Microsoft 365 Business Premium'
sel = df[(df['empresa'].astype(str).str.strip()==empresa_val) & (df['licenca'].astype(str).str.strip()==licenca_val)].copy()
sel['__centro_raw'] = sel['Centro de Custo'].astype(str).replace('nan','').fillna('').str.strip()
missing = sel[sel['__centro_raw']=='']
print('Total linhas do contrato:', len(sel))
print('Linhas com Centro de Custo vazio:', len(missing))
if len(missing)>0:
    outcols = ['empresa','licenca','Colaborador','Email','Centro de Custo','qtdLicenca','valorTotalLicenca']
    existing = [c for c in outcols if c in sel.columns]
    print(missing[existing].to_csv(index=False, sep=';'))
else:
    print('Nenhuma linha sem centro no arquivo original')
