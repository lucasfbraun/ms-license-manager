import os
import pandas as pd

EXCEL_FILE = 'LICENCIAMENTO MICROSOFT (1).xlsx'
UPDATED_EXCEL_FILE = 'LICENCIAMENTO_MICROSOFT_updated.xlsx'
use_file = UPDATED_EXCEL_FILE if os.path.exists(UPDATED_EXCEL_FILE) else EXCEL_FILE
print('Using', use_file)
df = pd.read_excel(use_file, sheet_name='Planilha1')
contratos = [{'empresa':'FLEXIVEL-JGS','licenca':'Microsoft 365 Business Premium'}]

# combine mask
masks = []
for c in contratos:
    emp = str(c.get('empresa','')).strip()
    lic = str(c.get('licenca','')).strip()
    m = (df['empresa'].astype(str).str.strip()==emp) & (df['licenca'].astype(str).str.strip()==lic)
    masks.append(m)
import functools, operator
mask_total = functools.reduce(operator.or_, masks)
dados = df[mask_total].copy()

# prepare
for col in ['qtdLicenca','valorTotalLicenca']:
    dados[col] = pd.to_numeric(dados[col], errors='coerce').fillna(0)

dados['__centro_raw'] = dados['Centro de Custo'].astype(str).replace('nan','').fillna('').str.strip()

def split_centro(val):
    if not val or pd.isna(val):
        return ('','')
    s = str(val)
    if '-' in s:
        parts = s.split('-',1)
        return (parts[0].strip(), parts[1].strip())
    return (s.strip(), '')

centros = dados['__centro_raw'].apply(lambda x: pd.Series(split_centro(x)))
centros.columns = ['centro_codigo','centro_nome']
dados = pd.concat([dados, centros], axis=1)

nome_col_existing = next((c for c in dados.columns if 'nome' in c.lower() and 'centro' in c.lower()), None)
print('found nome col:', nome_col_existing)
if nome_col_existing:
    dados['__nome_from_col'] = dados[nome_col_existing].astype(str).replace('nan','').fillna('').str.strip()
    dados['centro_nome'] = dados['centro_nome'].where(dados['centro_nome'] != '', dados['__nome_from_col'])

dados['centro_agrupar'] = dados['centro_codigo'].where(dados['centro_codigo'] != '', dados['__centro_raw'])

grp = dados.groupby(['centro_agrupar','centro_nome'], dropna=False).agg({'qtdLicenca':'sum','valorTotalLicenca':'sum'}).reset_index().rename(columns={'centro_agrupar':'centro_custo','qtdLicenca':'qtd_cc','valorTotalLicenca':'valor_cc','centro_nome':'nome_centro'})

print('\nGroup head:')
print(grp.head(30).to_string(index=False))

out = grp.copy()
empresas_sel = sorted(list(set([c.get('empresa','') for c in contratos])))
licencas_sel = sorted(list(set([c.get('licenca','') for c in contratos])))
empresas_label = '|'.join(empresas_sel)
licencas_label = '|'.join(licencas_sel)
out.insert(0,'licenca',licencas_label)
out.insert(0,'empresa',empresas_label)

out = out.rename(columns={'qtd_cc':'qtd (por centro de custo)','valor_cc':'valor por centro de custo','perc_cc':'% por centro de custo'})

# format
valor_total = grp['valor_cc'].sum()
out['% por centro de custo'] = grp['valor_cc'].apply(lambda v: (float(v)/float(valor_total)*100) if valor_total not in [0,None] else 0.0)

def fmt_val(v):
    try:
        return (f"{float(v):,.2f}".replace(',','X').replace('.',',').replace('X','.'))
    except Exception:
        return ''

out_fmt = out.copy()
out_fmt['valor por centro de custo'] = out_fmt['valor por centro de custo'].apply(fmt_val)
out_fmt['% por centro de custo'] = out_fmt['% por centro de custo'].apply(lambda x: f"{float(x):.2f}".replace('.',',') if pd.notna(x) else '')

print('\nOut formatted head:')
print(out_fmt.head(50).to_string(index=False))

# show whether nome_centro empty
print('\nRows where nome_centro empty:')
print(out_fmt[out_fmt['nome_centro'].isnull() | (out_fmt['nome_centro'].astype(str).str.strip()=='')])
