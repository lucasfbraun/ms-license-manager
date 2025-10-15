from flask import Flask, render_template_string, request, jsonify
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime

app = Flask(__name__)

# Caminho do arquivo Excel utilizado pelo dashboard
EXCEL_FILE = 'LICENCIAMENTO MICROSOFT (1).xlsx'

def load_data():
    """Carrega e processa os dados da planilha"""
    df = pd.read_excel(EXCEL_FILE, sheet_name='Planilha1')
    
    # Limpeza e conversão de dados
    df['valorAnual'] = pd.to_numeric(df['valorAnual'], errors='coerce')
    df['valorUnitarioMensal'] = pd.to_numeric(df['valorUnitarioMensal'], errors='coerce')
    df['qtdLicenca'] = pd.to_numeric(df['qtdLicenca'], errors='coerce')
    df['mesesContrato'] = pd.to_numeric(df['mesesContrato'], errors='coerce')
    df['proRata'] = pd.to_numeric(df['proRata'], errors='coerce')
    df['valorTotalLicenca'] = pd.to_numeric(df['valorTotalLicenca'], errors='coerce')
    
    # Converter datas
    df['DataCriacaoEmail'] = pd.to_datetime(df['DataCriacaoEmail'], errors='coerce')
    df['DataCriacaoFormatada'] = pd.to_datetime(df['DataCriacaoFormatada'], errors='coerce')
    df['inicioContrato'] = pd.to_datetime(df['inicioContrato'], errors='coerce')
    df['finalContrato'] = pd.to_datetime(df['finalContrato'], errors='coerce')
    
    return df

def apply_filters(df, filters):
    """Aplica filtros ao dataframe"""
    filtered_df = df.copy()
    
    if filters.get('empresa') and filters['empresa'] != 'Todas':
        filtered_df = filtered_df[filtered_df['empresa'] == filters['empresa']]
    
    if filters.get('estado') and filters['estado'] != 'Todos':
        filtered_df = filtered_df[filtered_df['estado'] == filters['estado']]
    
    if filters.get('setor') and filters['setor'] != 'Todos':
        filtered_df = filtered_df[filtered_df['setor'] == filters['setor']]
    
    if filters.get('centro_custo') and filters['centro_custo'] != 'Todos':
        filtered_df = filtered_df[filtered_df['Centro de Custo'] == filters['centro_custo']]
    
    if filters.get('licenca') and filters['licenca'] != 'Todas':
        filtered_df = filtered_df[filtered_df['licenca'] == filters['licenca']]
    
    if filters.get('modalidade') and filters['modalidade'] != 'Todas':
        filtered_df = filtered_df[filtered_df['modalidadeLicenca'] == filters['modalidade']]
    

    
    return filtered_df

def create_graphs(filters=None):
    """Cria todos os gráficos"""
    df = load_data()
    
    # Aplicar filtros se fornecidos
    if filters:
        df = apply_filters(df, filters)
    
    graphs = {}
    
    # KPIs
    kpis = {
        'total_gasto': f"R$ {df['valorTotalLicenca'].sum():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        'total_usuarios': len(df),
        'total_empresas': df['empresa'].nunique(),
        'total_licencas': int(df['qtdLicenca'].sum())
    }
    
    # 1. Gastos por Empresa

    gastos_empresa = df.groupby('empresa')['valorTotalLicenca'].sum().sort_values(ascending=False).head(15)
    fig1 = px.bar(x=gastos_empresa.values, y=gastos_empresa.index, orientation='h',
                  labels={'x': 'Gasto Total (R$)', 'y': 'Empresa'},
                  title='💼 Top 15 Empresas por Gasto')
    fig1.update_traces(marker_color='#609369')
    fig1.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(color='#333333', family='Cairo, sans-serif'),
        title_font=dict(size=18, color='#333333', family='Cairo')
    )
    graphs['empresas'] = fig1.to_html(full_html=False, div_id="graph1")
    
    # 2. Distribuição por Estado
    estado_counts = df.groupby('estado')['valorTotalLicenca'].sum()
    fig2 = px.pie(values=estado_counts.values, names=estado_counts.index,
                  title='🗺️ Distribuição por Estado', hole=0.4,
                  color_discrete_sequence=['#609369', '#026B69', '#7FB88A', '#014847', '#EEFF41', '#EEEEEE'])
    fig2.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(color='#333333', family='Cairo, sans-serif'),
        title_font=dict(size=18, color='#333333', family='Cairo')
    )
    graphs['estados'] = fig2.to_html(full_html=False, div_id="graph2")
    
    # 3. Top 10 Centros de Custo
    centro_custo = df.groupby('Centro de Custo')['valorTotalLicenca'].sum().sort_values(ascending=False).head(10)
    fig3 = px.bar(x=centro_custo.index, y=centro_custo.values,
                  labels={'x': 'Centro de Custo', 'y': 'Gasto Total (R$)'},
                  title='🏦 Top 10 Centros de Custo (Maior Gasto)')
    fig3.update_traces(marker_color='#026B69')
    fig3.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(color='#333333', family='Cairo, sans-serif'),
        title_font=dict(size=18, color='#333333', family='Cairo')
    )
    graphs['centro_custo'] = fig3.to_html(full_html=False, div_id="graph3")
    
    # 4. Licenças Mais Usadas
    try:
        licencas_count = df.groupby('licenca')['qtdLicenca'].sum().sort_values(ascending=False).head(10)
    except Exception as e:
        app.logger.error(f"Erro ao agrupar licencas: {e}")
        licencas_count = pd.Series(dtype='float64')

    app.logger.info(f"Licenças - linhas df: {len(df)}, colunas: {list(df.columns)}")
    app.logger.info(f"Licenças - tamanho licencas_count: {len(licencas_count)}")

    if licencas_count is not None and len(licencas_count) > 0:
        fig4 = px.bar(x=licencas_count.values, y=licencas_count.index, orientation='h',
                      labels={'x': 'Quantidade', 'y': 'Tipo de Licença'},
                      title='📊 Top 10 Licenças Mais Usadas')
        fig4.update_traces(marker_color='#026B69')
        fig4.update_layout(
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF',
            font=dict(color='#333333', family='Cairo, sans-serif'),
            title_font=dict(size=18, color='#333333', family='Cairo')
        )
        graphs['licencas'] = fig4.to_html(full_html=False, div_id="graph4")
    else:
        graphs['licencas'] = """
        <div class='alert alert-warning'>
            Não há dados suficientes para montar o gráfico de Licenças. Verifique se as colunas 'licenca' e 'qtdLicenca' possuem valores na planilha e se os filtros não zeraram os resultados.
        </div>
        """
    
    # 5. Modalidade de Licença
    modalidade = df.groupby('modalidadeLicenca')['valorTotalLicenca'].sum()
    fig5 = px.pie(values=modalidade.values, names=modalidade.index,
                  title='💳 Gastos por Modalidade de Licença', hole=0.3,
                  color_discrete_sequence=['#609369', '#026B69', '#7FB88A', '#014847', '#EEFF41'])
    fig5.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(color='#333333', family='Cairo, sans-serif'),
        title_font=dict(size=18, color='#333333', family='Cairo')
    )
    graphs['modalidade'] = fig5.to_html(full_html=False, div_id="graph5")
    
    # 6. Gastos por Setor
    setor = df.groupby('setor')['valorTotalLicenca'].sum().sort_values(ascending=False).head(15)
    fig6 = px.bar(x=setor.values, y=setor.index, orientation='h',
                  labels={'x': 'Gasto Total (R$)', 'y': 'Setor'},
                  title='🏢 Top 15 Setores por Gasto')
    fig6.update_traces(marker_color='#609369')
    fig6.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(color='#333333', family='Cairo, sans-serif'),
        title_font=dict(size=18, color='#333333', family='Cairo')
    )
    graphs['setor'] = fig6.to_html(full_html=False, div_id="graph6")
    
    # 7. Faturadores
    faturador = df.groupby('faturador')['valorTotalLicenca'].sum().dropna()
    if len(faturador) > 0:
        fig7 = px.pie(values=faturador.values, names=faturador.index,
                      title='🔄 Distribuição por Fornecedor (Faturador)',
                      color_discrete_sequence=['#609369', '#026B69', '#7FB88A', '#014847', '#EEFF41', '#EEEEEE'])
        fig7.update_layout(
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF',
            font=dict(color='#333333', family='Cairo, sans-serif'),
            title_font=dict(size=18, color='#333333', family='Cairo')
        )
        graphs['faturador'] = fig7.to_html(full_html=False, div_id="graph7")
    else:
        graphs['faturador'] = '<p class="text-muted">Sem dados de faturador</p>'
    
    # 8. Tabela de Contratos
    contratos_html = gerar_tabela_contratos(df)
    graphs['contratos'] = contratos_html
    
    return kpis, graphs

def gerar_tabela_contratos(df):
    """Gera tabela de contratos com alertas de vencimento"""
    from datetime import datetime, timedelta
    
    # Filtrar apenas registros com datas de contrato
    df_contratos = df[df['finalContrato'].notna()].copy()
    
    if len(df_contratos) == 0:
        return '<p class="text-muted">Nenhum contrato encontrado com data de vencimento.</p>'
    
    # Agrupar por empresa e licença para mostrar cada contrato
    contratos_detalhados = df_contratos.groupby(['empresa', 'licenca', 'modalidadeLicenca']).agg({
        'inicioContrato': 'min',
        'finalContrato': 'max',
        'valorTotalLicenca': 'sum',
        'qtdLicenca': 'sum'
    }).reset_index()
    
    # Ordenar por empresa e depois por data de vencimento
    contratos_detalhados = contratos_detalhados.sort_values(['empresa', 'finalContrato'])
    
    # Data atual
    hoje = datetime.now()
    sete_dias = hoje + timedelta(days=7)
    
    # Gerar HTML da tabela
    html = '''
    <div class="table-responsive">
        <table id="graph_contratos" class="table table-hover table-sm">
            <thead class="table-dark">
                <tr>
                    <th>Status</th>
                    <th>Empresa</th>
                    <th>Licença</th>
                    <th>Modalidade</th>
                    <th>Início</th>
                    <th>Vencimento</th>
                    <th>Dias Restantes</th>
                    <th>Qtd</th>
                    <th>Valor Total</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for _, row in contratos_detalhados.iterrows():
        empresa = row['empresa']
        licenca = row['licenca']
        modalidade = row['modalidadeLicenca']
        inicio = row['inicioContrato']
        fim = row['finalContrato']
        total = row['valorTotalLicenca']
        qtd_licencas = row['qtdLicenca']
        
        # Calcular dias restantes
        if pd.notna(fim):
            dias_restantes = (fim - hoje).days
            
            # Determinar classe CSS baseada no status
            if dias_restantes < 0:
                row_class = 'table-danger'
                status = '🔴 Vencido'
                dias_texto = f'{abs(dias_restantes)} dias atrás'
            elif dias_restantes <= 7:
                row_class = 'table-warning'
                status = '⚠️ Vence em breve'
                dias_texto = f'{dias_restantes} dias'
            elif dias_restantes <= 30:
                row_class = 'table-info'
                status = '🔵 Atenção'
                dias_texto = f'{dias_restantes} dias'
            else:
                row_class = ''
                status = '✅ OK'
                dias_texto = f'{dias_restantes} dias'
            
            inicio_formatado = inicio.strftime('%d/%m/%Y') if pd.notna(inicio) else 'N/A'
            fim_formatado = fim.strftime('%d/%m/%Y') if pd.notna(fim) else 'N/A'
            total_formatado = f"R$ {total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            html += f'''
                <tr class="{row_class}">
                    <td><strong>{status}</strong></td>
                    <td><strong>{empresa}</strong></td>
                    <td>{licenca}</td>
                    <td><small>{modalidade}</small></td>
                    <td>{inicio_formatado}</td>
                    <td><strong>{fim_formatado}</strong></td>
                    <td><strong>{dias_texto}</strong></td>
                    <td>{int(qtd_licencas)}</td>
                    <td>{total_formatado}</td>
                </tr>
            '''
    
    html += '''
            </tbody>
        </table>
    </div>
    
    <div class="mt-3">
        <small>
            <span class="badge bg-danger">🔴 Vencido</span> - Contrato já venceu<br>
            <span class="badge bg-warning text-dark">⚠️ Vence em breve</span> - Vence em até 7 dias<br>
            <span class="badge bg-info">🔵 Atenção</span> - Vence em até 30 dias<br>
            <span class="badge bg-success">✅ OK</span> - Vence em mais de 30 dias
        </small>
    </div>
    '''
    
    return html

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerenciamento - Licenciamento Microsoft</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap');
        
        :root {
            /* Nova Paleta de Cores */
            --primary: #609369;
            --card-bg: #026B69;
            --page-bg: #013938;
            --title-color: #EEEEEE;
            --body-color: #FFFFFF;
            --accent-light: #7FB88A;
            --accent-dark: #014847;
        }
        
        body {
            background-color: var(--page-bg);
            font-family: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: var(--body-color);
            line-height: 1.6;
        }
        
        .dashboard-header {
            background: linear-gradient(135deg, var(--card-bg) 0%, var(--primary) 100%);
            color: var(--body-color);
            padding: 50px;
            border-radius: 0;
            margin-bottom: 40px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            position: relative;
        }
        
        .dashboard-logo {
            position: absolute;
            top: 15px;
            left: 40px;
            height: 120px;
            width: auto;
            filter: brightness(0) invert(1);
            opacity: 0.95;
            transition: all 0.3s ease;
        }
        
        .dashboard-logo:hover {
            opacity: 1;
            transform: scale(1.05);
        }
        
        .dashboard-header h1 {
            font-family: 'Cairo', sans-serif;
            font-weight: 700;
            margin-bottom: 12px;
            font-size: 2.5rem;
            letter-spacing: -0.5px;
            margin-left: 150px;
            color: var(--title-color);
        }
        
        .dashboard-header p {
            font-family: 'Cairo', sans-serif;
            font-size: 1.2rem;
            opacity: 0.95;
            font-weight: 500;
            margin-left: 150px;
            color: var(--body-color);
        }
        
        .dashboard-header small {
            opacity: 0.85;
            font-size: 0.9rem;
            margin-left: 150px;
            color: var(--body-color);
        }
        
        .kpi-card {
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            margin-bottom: 24px;
            border: none;
            overflow: hidden;
            background: #FFFFFF;
        }
        
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
        }
        
        .kpi-card.bg-success {
            background: linear-gradient(135deg, var(--primary) 0%, #7FB88A 100%) !important;
            color: #FFFFFF;
        }
        
        .kpi-card.bg-primary {
            background: linear-gradient(135deg, var(--card-bg) 0%, #038280 100%) !important;
            color: #FFFFFF;
        }
        
        .kpi-card.bg-info {
            background: linear-gradient(135deg, #014847 0%, var(--card-bg) 100%) !important;
            color: #FFFFFF;
        }
        
        .kpi-card.bg-warning {
            background: linear-gradient(135deg, var(--primary) 0%, #7FB88A 100%) !important;
            color: #FFFFFF !important;
        }
        
        .kpi-card .card-body h6 {
            font-family: 'Cairo', sans-serif;
            font-weight: 700;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            opacity: 0.9;
            color: #FFFFFF;
        }
        
        .kpi-card .card-body h2 {
            font-family: 'Cairo', sans-serif;
            font-weight: 700;
            font-size: 2.8rem;
            margin: 18px 0;
            letter-spacing: -1px;
            color: #FFFFFF;
        }
        
        .kpi-card .card-body small {
            opacity: 0.85;
            font-size: 0.85rem;
            color: #FFFFFF;
        }
        
        .card-custom {
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            margin-bottom: 28px;
            border: none;
            background: #FFFFFF;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .card-custom:hover {
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
            transform: translateY(-2px);
        }
        
        .card-custom .card-body {
            padding: 28px;
        }
        
        .card-custom h5 {
            font-family: 'Cairo', sans-serif;
            color: var(--primary);
            font-weight: 700;
            margin-bottom: 24px;
            font-size: 1.3rem;
        }
        
        .filter-section {
            background: #FFFFFF;
            padding: 28px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            margin-bottom: 30px;
            border-top: 3px solid var(--primary);
        }
        
        .filter-section h5 {
            font-family: 'Cairo', sans-serif;
            color: var(--primary);
            font-weight: 700;
            margin-bottom: 24px;
            font-size: 1.2rem;
        }
        
        .filter-label {
            font-family: 'Cairo', sans-serif;
            font-weight: 600;
            color: #333333;
            margin-bottom: 8px;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .form-select {
            border: 1px solid #DDDDDD;
            border-radius: 6px;
            padding: 10px 14px;
            transition: all 0.3s;
            background-color: #FAFAFA;
            color: #333333;
        }
        
        .form-select:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 0.25rem rgba(96, 147, 105, 0.2);
            outline: none;
        }
        
        .btn-filter {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, var(--primary) 0%, #7FB88A 100%);
            border: none;
            padding: 12px 32px;
            font-weight: 700;
            border-radius: 6px;
            transition: all 0.2s;
            color: var(--body-color);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.9rem;
        }
        
        .btn-filter:hover {
            background: linear-gradient(135deg, #7FB88A 0%, var(--primary) 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(96, 147, 105, 0.4);
        }
        
        .btn-clear {
            font-family: 'Cairo', sans-serif;
            background: var(--accent-dark);
            border: 1px solid var(--primary);
            padding: 12px 32px;
            font-weight: 700;
            border-radius: 6px;
            transition: all 0.2s;
            color: var(--body-color);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.9rem;
        }
        
        .btn-clear:hover {
            background: var(--card-bg);
            border-color: var(--primary);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(96, 147, 105, 0.3);
        }
        
        .user-card {
            background: #FAFAFA;
            border-left: 5px solid var(--primary);
            padding: 20px;
            margin-bottom: 14px;
            border-radius: 10px;
            transition: all 0.3s;
        }
        
        .user-card:hover {
            background: #FFFFFF;
            border-left-color: #7FB88A;
            box-shadow: 0 4px 12px rgba(96, 147, 105, 0.3);
            transform: translateX(8px);
        }
        
        .badge-licenca {
            font-family: 'Cairo', sans-serif;
            cursor: pointer;
            transition: all 0.3s;
            background: var(--primary) !important;
            padding: 10px 18px;
            font-size: 0.95rem;
            border-radius: 8px;
            font-weight: 600;
        }
        
        .badge-licenca:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 12px rgba(0, 151, 167, 0.5);
            background: var(--accent1) !important;
        }
        
        .table-danger {
            background-color: #ffebee !important;
            font-weight: 600;
            border-left: 5px solid #f44336;
            color: #333333;
        }
        
        .table-warning {
            background-color: #fff9e6 !important;
            font-weight: 600;
            border-left: 5px solid var(--primary);
            color: #333333;
        }
        
        .table-info {
            background-color: #e1f5fe !important;
            border-left: 5px solid var(--card-bg);
            color: #333333;
        }
        
        .table-danger:hover, .table-warning:hover, .table-info:hover {
            opacity: 0.88;
        }
        
        .table-dark {
            background: linear-gradient(135deg, var(--card-bg) 0%, var(--primary) 100%) !important;
            color: var(--body-color);
        }
        
        .table-dark th {
            font-family: 'Cairo', sans-serif;
            border: none !important;
            padding: 16px !important;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.8px;
        }
        
        .modal-header {
            background: linear-gradient(135deg, var(--card-bg) 0%, var(--primary) 100%);
            color: var(--body-color);
            border-radius: 8px 8px 0 0;
        }
        
        .modal-header .btn-close {
            filter: brightness(0) invert(1);
        }
        
        .modal-content {
            border-radius: 8px;
            border: none;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
            background-color: #FFFFFF;
            color: #333333;
        }
        
        .badge.bg-danger {
            background: #f44336 !important;
            font-family: 'Cairo', sans-serif;
        }
        
        .badge.bg-warning {
            background: var(--primary) !important;
            color: var(--body-color) !important;
            font-family: 'Cairo', sans-serif;
            font-weight: 700;
        }
        
        .badge.bg-info {
            background: var(--card-bg) !important;
            font-family: 'Cairo', sans-serif;
        }
        
        .badge.bg-success {
            background: #4CAF50 !important;
            font-family: 'Cairo', sans-serif;
        }
        
        /* Animações */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .card-custom, .kpi-card {
            animation: slideIn 0.5s ease-out;
        }
        
        /* Scrollbar personalizada */
        ::-webkit-scrollbar {
            width: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #F5F5F5;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--primary);
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #7FB88A;
        }
        
        .table {
            color: #333333;
            background-color: #FFFFFF;
        }
        
        .table-hover tbody tr:hover {
            background-color: rgba(96, 147, 105, 0.1) !important;
        }
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <!-- Header -->
        <div class="dashboard-header text-center">
            <img src="/static/logo.png" alt="Logo" class="dashboard-logo">
            <h1 class="mb-2">📊 Dashboard de Licenciamento Microsoft</h1>
            <p class="mb-0">Análise Completa de Licenças e Custos</p>
            <small>Última atualização: {{ update_time }}</small>
        </div>
        
        <!-- Filtros -->
        <div class="filter-section">
            <h5 class="mb-4"><i class="bi bi-funnel"></i> 🔍 Filtros</h5>
            <form method="GET" action="/">
                <div class="row">
                    <div class="col-md-2">
                        <label class="filter-label">Empresa</label>
                        <select name="empresa" class="form-select form-select-sm">
                            <option value="Todas" {% if current_filters.empresa == 'Todas' %}selected{% endif %}>Todas</option>
                            {% for empresa in filter_options.empresas %}
                            <option value="{{ empresa }}" {% if current_filters.empresa == empresa %}selected{% endif %}>{{ empresa }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <div class="col-md-2">
                        <label class="filter-label">Estado</label>
                        <select name="estado" class="form-select form-select-sm">
                            <option value="Todos" {% if current_filters.estado == 'Todos' %}selected{% endif %}>Todos</option>
                            {% for estado in filter_options.estados %}
                            <option value="{{ estado }}" {% if current_filters.estado == estado %}selected{% endif %}>{{ estado }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <div class="col-md-2">
                        <label class="filter-label">Setor</label>
                        <select name="setor" class="form-select form-select-sm">
                            <option value="Todos" {% if current_filters.setor == 'Todos' %}selected{% endif %}>Todos</option>
                            {% for setor in filter_options.setores %}
                            <option value="{{ setor }}" {% if current_filters.setor == setor %}selected{% endif %}>{{ setor }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <div class="col-md-2">
                        <label class="filter-label">Centro de Custo</label>
                        <select name="centro_custo" class="form-select form-select-sm">
                            <option value="Todos" {% if current_filters.centro_custo == 'Todos' %}selected{% endif %}>Todos</option>
                            {% for cc in filter_options.centros_custo %}
                            <option value="{{ cc }}" {% if current_filters.centro_custo == cc %}selected{% endif %}>{{ cc }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <div class="col-md-2">
                        <label class="filter-label">Licença</label>
                        <select name="licenca" class="form-select form-select-sm">
                            <option value="Todas" {% if current_filters.licenca == 'Todas' %}selected{% endif %}>Todas</option>
                            {% for licenca in filter_options.licencas %}
                            <option value="{{ licenca }}" {% if current_filters.licenca == licenca %}selected{% endif %}>{{ licenca }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <div class="col-md-2">
                        <label class="filter-label">Modalidade</label>
                        <select name="modalidade" class="form-select form-select-sm">
                            <option value="Todas" {% if current_filters.modalidade == 'Todas' %}selected{% endif %}>Todas</option>
                            {% for mod in filter_options.modalidades %}
                            <option value="{{ mod }}" {% if current_filters.modalidade == mod %}selected{% endif %}>{{ mod }}</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
                
                <div class="row mt-3">
                    <div class="col-md-12 text-end">
                        <button type="submit" class="btn btn-primary btn-filter">🔍 Aplicar Filtros</button>
                        <a href="/" class="btn btn-secondary btn-clear">🔄 Limpar Filtros</a>
                    </div>
                </div>
            </form>
        </div>
        
        <!-- KPI Cards -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card kpi-card bg-success text-white">
                    <div class="card-body text-center">
                        <h6>💰 Gasto Total</h6>
                        <h2>{{ kpis.total_gasto }}</h2>
                        <small>Total investido em licenças</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card kpi-card bg-primary text-white">
                    <div class="card-body text-center">
                        <h6>👥 Total de Usuários</h6>
                        <h2>{{ kpis.total_usuarios }}</h2>
                        <small>Usuários com licenças</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card kpi-card bg-info text-white">
                    <div class="card-body text-center">
                        <h6>🏢 Empresas</h6>
                        <h2>{{ kpis.total_empresas }}</h2>
                        <small>Empresas cadastradas</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card kpi-card bg-warning text-white">
                    <div class="card-body text-center">
                        <h6>📋 Licenças</h6>
                        <h2>{{ kpis.total_licencas }}</h2>
                        <small>Total de licenças ativas</small>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Gráficos -->
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card card-custom">
                    <div class="card-body">
                        {{ graphs.empresas | safe }}
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card card-custom">
                    <div class="card-body">
                        {{ graphs.estados | safe }}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-12 mb-4">
                <div class="card card-custom">
                    <div class="card-body">
                        {{ graphs.centro_custo | safe }}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card card-custom">
                    <div class="card-body">
                        <h5 class="mb-3">📊 Top 10 Licenças Mais Usadas 
                            <small class="text-muted">(Clique em uma licença para ver usuários)</small>
                        </h5>
                        {{ graphs.licencas | safe }}
                        <div id="licencasList" class="mt-3"></div>
                        <script>
                        (function() {
                            const listEl = document.getElementById('licencasList');
                            function renderFallbackList(gd) {
                                try {
                                    const labels = (gd && gd.data && gd.data[0] && gd.data[0].y) || [];
                                    if (!labels || labels.length === 0 || !listEl) return;
                                    let html = '<div class="d-flex flex-wrap gap-2">';
                                    labels.forEach(lbl => {
                                        const text = String(lbl);
                                        html += `<button type="button" class="btn btn-sm" style="border:1px solid #026B69;color:#026B69" onclick="window.mostrarUsuarios('${text.replace(/'/g, "&#39;")}')">${text}</button>`;
                                    });
                                    html += '</div>';
                                    listEl.innerHTML = html;
                                } catch (e) { console.warn('Falha ao montar lista fallback de licenças', e); }
                            }

                            function bindClick() {
                                const gd = document.getElementById('graph4');
                                if (!gd) return false;
                                if (typeof gd.on === 'function') {
                                    try {
                                        renderFallbackList(gd);
                                        gd.on('plotly_click', function(evt) {
                                            try {
                                                const pt = evt.points && evt.points[0];
                                                const licenca = String((pt && (pt.y ?? pt.label ?? pt.text)) || '');
                                                console.log('[licencas] clique no gráfico:', licenca, pt);
                                                if (licenca) { window.mostrarUsuarios(licenca); }
                                            } catch (e) {
                                                console.error('Erro ao capturar clique na licença:', e);
                                            }
                                        });
                                        gd.style.cursor = 'pointer';
                                    } catch (e) { console.warn('Falha ao vincular click no gráfico', e); }
                                    return true;
                                }
                                return false;
                            }
                            if (!bindClick()) {
                                let attempts = 0;
                                const iv = setInterval(() => {
                                    attempts++;
                                    if (bindClick() || attempts > 25) clearInterval(iv);
                                }, 200);
                            }
                        })();
                        </script>
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card card-custom">
                    <div class="card-body">
                        {{ graphs.modalidade | safe }}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card card-custom">
                    <div class="card-body">
                        {{ graphs.setor | safe }}
                    </div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card card-custom">
                    <div class="card-body">
                        {{ graphs.faturador | safe }}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Contratos -->
        <div class="row">
            <div class="col-md-12 mb-4">
                <div class="card card-custom">
                    <div class="card-body">
                        <h5 class="card-title">📋 Controle de Contratos por Empresa</h5>
                        <p class="text-muted">Acompanhamento de vencimentos e renovações</p>
                        <div class="mb-3">
                            <input type="text" id="pesquisa-contratos" class="form-control" placeholder="Pesquisar na tabela...">
                        </div>
                        {{ graphs.contratos | safe }}
                        <script>
                        (function() {
                            const input = document.getElementById('pesquisa-contratos');
                            if (input) {
                                input.addEventListener('keyup', function() {
                                    const termo = input.value.toLowerCase();
                                    document.querySelectorAll('#graph_contratos tbody tr').forEach(function(row) {
                                        const texto = row.textContent.toLowerCase();
                                        row.style.display = texto.includes(termo) ? '' : 'none';
                                    });
                                });
                            }
                        })();
                        </script>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modal para mostrar usuários -->
    <div class="modal fade" id="modalUsuarios" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title" id="modalTitle">👥 Usuários da Licença</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="modalBody" style="max-height: 600px; overflow-y: auto;">
                    <div class="text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Carregando...</span>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                </div>
            </div>
        </div>
    </div>

        <script>
    window.mostrarUsuarios = function(licenca) {
            const modalEl = document.getElementById('modalUsuarios');
            let modal = null;
            try {
                if (window.bootstrap && bootstrap.Modal) {
                    modal = new bootstrap.Modal(modalEl);
                }
            } catch (e) {
                console.warn('Bootstrap Modal não disponível, aplicando fallback:', e);
            }
            document.getElementById('modalTitle').textContent = `👥 Usuários da Licença: ${licenca}`;
            document.getElementById('modalBody').innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Carregando...</span>
                    </div>
                    <p class="mt-2">Carregando usuários...</p>
                </div>
            `;
            if (modal) {
                modal.show();
            } else {
                // Fallback simples caso Bootstrap não esteja disponível
                modalEl.classList.add('show');
                modalEl.style.display = 'block';
                modalEl.removeAttribute('aria-hidden');
                modalEl.setAttribute('aria-modal', 'true');
            }
            fetch(`/api/usuarios/${encodeURIComponent(licenca)}`)
                .then(response => {
                    if (!response.ok) {
                        console.error('Falha HTTP ao buscar usuários:', response.status, response.statusText);
                        throw new Error('HTTP ' + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Dados recebidos de /api/usuarios:', data);
                    let html = `
                        <div class="alert alert-info">
                            <strong>Total de usuários com esta licença: ${data.total_usuarios}</strong>
                        </div>
                    `;
                    
                    if (data.usuarios.length === 0) {
                        html += '<p class="text-muted">Nenhum usuário encontrado para esta licença.</p>';
                    } else {
                        data.usuarios.forEach(usuario => {
                            html += `
                                <div class="user-card">
                                    <div class="row">
                                        <div class="col-md-8">
                                            <h6 class="mb-1"><strong>${usuario['Colaborador'] || usuario.colaborador || ''}</strong></h6>
                                            <p class="mb-1 text-muted small">
                                                📧 ${usuario['Email'] || usuario.email || 'Sem email'}<br>
                                                🏢 ${usuario['Empresa'] || usuario.empresa || ''}<br>
                                                🏭 Setor: ${usuario['Setor'] || usuario.setor || ''}<br>
                                                🗺️ Estado: ${usuario['Estado'] || usuario.estado || ''}<br>
                                                🏦 Centro de Custo: ${usuario['Centro de Custo'] || usuario.centro_custo || ''}
                                            </p>
                                        </div>
                                        <div class="col-md-4 text-end">
                                            <p class="mb-1"><strong>Qtd:</strong> ${usuario['Quantidade'] ?? usuario.quantidade ?? ''}</p>
                                            <p class="mb-1"><strong>Valor Unit:</strong> R$ ${(usuario['Valor Unitário'] ?? usuario.valor_unitario ?? 0).toFixed ? (usuario['Valor Unitário'] ?? usuario.valor_unitario).toFixed(2) : Number(usuario['Valor Unitário'] ?? usuario.valor_unitario ?? 0).toFixed(2)}</p>
                                            <p class="mb-0"><strong>Total:</strong> R$ ${(usuario['Total'] ?? usuario.total ?? 0).toFixed ? (usuario['Total'] ?? usuario.total).toFixed(2) : Number(usuario['Total'] ?? usuario.total ?? 0).toFixed(2)}</p>
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                    }
                    
                    document.getElementById('modalBody').innerHTML = html;
                })
                .catch(error => {
                    console.error('Erro ao carregar usuários:', error);
                    document.getElementById('modalBody').innerHTML = `
                        <div class="alert alert-danger">
                            Erro ao carregar usuários. Por favor, tente novamente.
                        </div>
                    `;
                });
    }
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    # Obter filtros da URL
    filters = {
        'empresa': request.args.get('empresa', 'Todas'),
        'estado': request.args.get('estado', 'Todos'),
        'setor': request.args.get('setor', 'Todos'),
        'centro_custo': request.args.get('centro_custo', 'Todos'),
        'licenca': request.args.get('licenca', 'Todas'),
        'modalidade': request.args.get('modalidade', 'Todas')
    }
    
    # Carregar dados originais para opções de filtro
    df_original = load_data()
    
    # Opções para os filtros
    filter_options = {
        'empresas': sorted(df_original['empresa'].dropna().unique()),
        'estados': sorted(df_original['estado'].dropna().unique()),
        'setores': sorted(df_original['setor'].dropna().unique()),
        'centros_custo': sorted(df_original['Centro de Custo'].dropna().unique()),
        'licencas': sorted(df_original['licenca'].dropna().unique()),
        'modalidades': sorted(df_original['modalidadeLicenca'].dropna().unique())
    }
    
    # Criar gráficos e KPIs
    kpis, graphs = create_graphs(filters)
    
    # Renderizar template
    return render_template_string(HTML_TEMPLATE, kpis=kpis, graphs=graphs,
                                  filter_options=filter_options, current_filters=filters,
                                  update_time=datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

@app.route('/api/usuarios/<licenca>', methods=['GET'])
def api_usuarios(licenca):
    """API para retornar usuários de uma licença específica"""
    df = load_data()
    licenca_norm = (licenca or '').strip().lower()
    app.logger.info(f"/api/usuarios chamada para licença: '{licenca}' (norm='{licenca_norm}')")
    
    # Filtrar dados pela licença (case-insensitive, ignorando espaços)
    dados_licenca = df[df['licenca'].astype(str).str.strip().str.lower() == licenca_norm]
    
    # Obter lista de usuários
    usuarios = dados_licenca[['nomeColaborador', 'email', 'empresa', 'setor', 'estado', 'Centro de Custo',
                               'qtdLicenca', 'valorUnitarioMensal', 'valorTotalLicenca']]
    
    # Renomear colunas para o formato desejado na resposta
    usuarios = usuarios.rename(columns={
    'nomeColaborador': 'Colaborador',
        'email': 'Email',
        'empresa': 'Empresa',
        'setor': 'Setor',
        'estado': 'Estado',
        'Centro de Custo': 'Centro de Custo',
        'qtdLicenca': 'Quantidade',
        'valorUnitarioMensal': 'Valor Unitário',
        'valorTotalLicenca': 'Total'
    })
    
    # Converter para lista de dicionários
    usuarios_list = usuarios.to_dict(orient='records')
    
    # Contar total de usuários
    total_usuarios = len(usuarios_list)
    
    return jsonify({'total_usuarios': total_usuarios, 'usuarios': usuarios_list})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
