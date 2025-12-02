import pandas as pd
EXCEL_FILE = 'LICENCIAMENTO MICROSOFT (1).xlsx'
df = pd.read_excel(EXCEL_FILE, sheet_name='Planilha1')
empresa_val = 'FLEXIVEL-JGS'
licenca_val = 'Microsoft 365 Business Premium'
sel = df[(df['empresa'].astype(str).str.strip()==empresa_val) & (df['licenca'].astype(str).str.strip()==licenca_val)].copy()
sel['__centro_raw'] = sel['Centro de Custo'].astype(str).replace('nan','').fillna('').str.strip()
missing = sel[sel['__centro_raw']=='']
print('Colunas disponíveis:', list(sel.columns))
print('\nMostrando linhas sem Centro de Custo:')
print(missing.to_csv(index=True, sep=';', encoding='utf-8'))
# salvar detalhes
missing.to_csv('missing_centros_full_original.csv', index=True, sep=';', encoding='utf-8')
print('\nArquivo salvo: missing_centros_full_original.csv')
