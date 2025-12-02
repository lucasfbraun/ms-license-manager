import os
import pandas as pd

EXCEL_FILE = 'LICENCIAMENTO MICROSOFT (1).xlsx'
UPDATED_EXCEL_FILE = 'LICENCIAMENTO_MICROSOFT_updated.xlsx'
use_file = UPDATED_EXCEL_FILE if os.path.exists(UPDATED_EXCEL_FILE) else EXCEL_FILE

print('Usando arquivo:', use_file)

df = pd.read_excel(use_file, sheet_name='Planilha1')

# normalize columns
cols = [c.lower() for c in df.columns]
# find actual column names
empresa_col = next((c for c in df.columns if c.lower()=='empresa'), None)
licenca_col = next((c for c in df.columns if c.lower()=='licenca'), None)
centro_col = next((c for c in df.columns if c.lower()=='centro de custo' or c.lower()=='centro_custo'), None)
colab_col = next((c for c in df.columns if c.lower()=='colaborador' or c.lower()=='colaborador '), None)
email_col = next((c for c in df.columns if c.lower() in ('email','e-mail')), None)
valor_col = next((c for c in df.columns if c.lower()=='valortotallicenca' or c.lower()=='valortotallicenca' or c.lower()=='valorTotalLicenca'.lower()), None)

print('colunas detectadas:', empresa_col, licenca_col, centro_col, colab_col, email_col, valor_col)

# filter for target contract
empresa_val = 'FLEXIVEL-JGS'
licenca_val = 'Microsoft 365 Business Premium'

sel = df[(df[empresa_col].astype(str).str.strip()==empresa_val) & (df[licenca_col].astype(str).str.strip()==licenca_val)].copy()

# normalize centro
sel['__centro_raw'] = sel[centro_col].astype(str).replace('nan','').fillna('').str.strip()

missing = sel[sel['__centro_raw']=='']

print('\nTotal linhas do contrato:', len(sel))
print('Linhas com Centro de Custo vazio:', len(missing))

if len(missing)>0:
    cols_out = [empresa_col, licenca_col, colab_col, email_col, centro_col, 'qtdLicenca', 'valorTotalLicenca']
    cols_out = [c for c in cols_out if c in sel.columns]
    print('\nDetalhe das linhas sem Centro de Custo:')
    print(missing[cols_out].to_csv(index=False, sep=';'))
else:
    print('Nenhuma linha sem Centro de Custo encontrada para esse contrato.')
