import pandas as pd
import openpyxl

# Carregar a planilha
excel_file = 'LICENCIAMENTO MICROSOFT (1).xlsx'

# Ler todas as abas
xls = pd.ExcelFile(excel_file)
print("Abas disponíveis:", xls.sheet_names)
print("\n" + "="*80 + "\n")

# Analisar cada aba
for sheet_name in xls.sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    print(f"ABA: {sheet_name}")
    print(f"Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
    print(f"Colunas: {list(df.columns)}")
    print(f"\nPrimeiras linhas:")
    print(df.head(3))
    print("\n" + "="*80 + "\n")
