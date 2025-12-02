#!/usr/bin/env python3
import os
import re
import sys
import pandas as pd

# Paths
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT = os.path.join(ROOT, 'LICENCIAMENTO MICROSOFT (1).xlsx')
OUTPUT = os.path.join(ROOT, 'LICENCIAMENTO_MICROSOFT_updated.xlsx')
SHEET_NAME = 'Planilha1'

def split_centrocusto_val(v):
    if pd.isna(v):
        return ('', '')
    s = str(v).strip()
    # pattern: everything before first '-' is codigo, after is nome
    m = re.match(r"^(.*?)\s*-\s*(.*)$", s)
    if m:
        codigo = m.group(1).strip()
        nome = m.group(2).strip()
        return (codigo, nome)
    else:
        # no dash: try to detect if ends with non-digit word separated by space
        # but per spec, keep whole in codigo and nome empty
        return (s, '')


def main():
    if not os.path.exists(INPUT):
        print(f"Arquivo de entrada não encontrado: {INPUT}")
        sys.exit(1)

    print(f"Lendo {INPUT} (planilha '{SHEET_NAME}')...")
    try:
        df = pd.read_excel(INPUT, sheet_name=SHEET_NAME, dtype=str)
    except Exception as e:
        print('Erro ao ler o Excel:', e)
        sys.exit(1)

    col = 'Centro de Custo'
    if col not in df.columns:
        print(f"Coluna '{col}' não encontrada na planilha. Colunas disponiveis:")
        print(df.columns.tolist())
        sys.exit(1)

    # Apply split
    print('Separando coluna Centro de Custo em duas colunas...')
    resultados = df[col].apply(split_centrocusto_val)
    df['Centro de Custo'] = resultados.apply(lambda x: x[0])
    df['Nome Centro de Custo'] = resultados.apply(lambda x: x[1])

    # Save to new workbook
    print(f'Gravando arquivo de saída: {OUTPUT}')
    try:
        df.to_excel(OUTPUT, index=False, sheet_name=SHEET_NAME)
    except Exception as e:
        print('Erro ao gravar o Excel:', e)
        sys.exit(1)

    print('Concluído. Arquivo gerado:', OUTPUT)

if __name__ == '__main__':
    main()
