import os
import pandas as pd

EXCEL_FILE = 'LICENCIAMENTO MICROSOFT (1).xlsx'
UPDATED_EXCEL_FILE = 'LICENCIAMENTO_MICROSOFT_updated.xlsx'
use_file = UPDATED_EXCEL_FILE if os.path.exists(UPDATED_EXCEL_FILE) else EXCEL_FILE
print('Using', use_file)
df = pd.read_excel(use_file, sheet_name='Planilha1')

empresa_val = 'FLEXIVEL-JGS'
licenca_val = 'Microsoft 365 Business Premium'
sel = df[(df['empresa'].astype(str).str.strip()==empresa_val) & (df['licenca'].astype(str).str.strip()==licenca_val)].copy()
sel['__centro_raw'] = sel['Centro de Custo'].astype(str).replace('nan','').fillna('').str.strip()

# detect nome col
nome_col_existing = next((c for c in sel.columns if 'nome' in c.lower() and 'centro' in c.lower()), None)
if nome_col_existing:
    sel['__nome_from_col'] = sel[nome_col_existing].astype(str).replace('nan','').fillna('').str.strip()
else:
    sel['__nome_from_col'] = ''

# split

def split_centro(val):
    if not val or pd.isna(val):
        return ('', '')
    s = str(val)
    if '-' in s:
        parts = s.split('-', 1)
        return (parts[0].strip(), parts[1].strip())
    return (s.strip(), '')

centros = sel['__centro_raw'].apply(lambda x: pd.Series(split_centro(x)))
centros.columns = ['centro_codigo', 'centro_nome']
sel = pd.concat([sel, centros], axis=1)
sel['centro_nome'] = sel['centro_nome'].where(sel['centro_nome'] != '', sel['__nome_from_col'])
sel['centro_agrupar'] = sel['centro_codigo'].where(sel['centro_codigo'] != '', sel['__centro_raw'])

pairs = sel.groupby(['__centro_raw','centro_codigo','centro_nome','__nome_from_col']).size().reset_index(name='count')
print(pairs.to_string(index=False))
