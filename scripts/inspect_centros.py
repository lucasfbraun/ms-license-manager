import os
import pandas as pd
UPDATED_EXCEL_FILE = 'LICENCIAMENTO_MICROSOFT_updated.xlsx'
EXCEL_FILE = 'LICENCIAMENTO MICROSOFT (1).xlsx'
use_file = UPDATED_EXCEL_FILE if os.path.exists(UPDATED_EXCEL_FILE) else EXCEL_FILE
print('Usando arquivo:', use_file)
df = pd.read_excel(use_file, sheet_name='Planilha1')
print('Colunas:', df.columns.tolist())

# show sample values for Centro de Custo and Nome Centro de Custo if present
centro_col = next((c for c in df.columns if c.lower()=='centro de custo' or c.lower()=='centro_custo'), None)
nome_col = next((c for c in df.columns if 'nome' in c.lower() and 'centro' in c.lower()), None)
print('Centro col:', centro_col)
print('Nome centro col:', nome_col)

if centro_col:
    s = df[centro_col].astype(str).replace('nan','').fillna('').str.strip()
    print('\nExemplos (first 30 unique non-empty Centros):')
    vals = [v for v in pd.unique(s) if v]
    for v in vals[:30]:
        print('-', repr(v))
    empty_count = (s== '').sum()
    print('\nTotal linhas:', len(s), 'vazios em Centro de Custo:', empty_count)

if nome_col:
    s2 = df[nome_col].astype(str).replace('nan','').fillna('').str.strip()
    print('\nExemplos (first 30 unique Nome Centro):')
    for v in pd.unique(s2)[:30]:
        print('-', repr(v))
    empty_count2 = (s2=='').sum()
    print('\nTotal linhas:', len(s2), 'vazios em Nome Centro:', empty_count2)
else:
    print('\nNenhuma coluna de nome de centro detectada.')
