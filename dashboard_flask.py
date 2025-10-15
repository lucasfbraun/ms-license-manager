from flask import Flask, render_template_string, request, jsonify
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime

app = Flask(__name__)

EXCEL_FILE = 'LICENCIAMENTO MICROSOFT (1).xlsx'

def load_data():
    """Carrega e processa os dados da planilha"""
    df = pd.read_excel(EXCEL_FILE, sheet_name='Planilha1')
    
    # Limpeza e conversão de dados
    df['valor unitario'] = pd.to_numeric(df['valor unitario'], errors='coerce')
    df['quantidade de licenças'] = pd.to_numeric(df['quantidade de licenças'], errors='coerce')
    df['total'] = pd.to_numeric(df['total'], errors='coerce')
    
    # Calcular total se estiver vazio
    df['total'] = df.apply(
        lambda row: row['valor unitario'] * row['quantidade de licenças'] 
        if pd.isna(row['total']) else row['total'], 
        axis=1
    )
    
    # Converter datas
    df['data criação do e-mail'] = pd.to_datetime(df['data criação do e-mail'], errors='coerce')
    df['inicio contrato'] = pd.to_datetime(df['inicio contrato'], errors='coerce')
    df['final contrato'] = pd.to_datetime(df['final contrato'], errors='coerce')
    
    return df

def apply_filters(df, filters):
    """Aplica filtros ao dataframe"""
    filtered_df = df.copy()
    
    if filters.get('empresa') and filters['empresa'] != 'Todas':
        filtered_df = filtered_df[filtered_df['Empresa'] == filters['empresa']]
    
    if filters.get('estado') and filters['estado'] != 'Todos':
        filtered_df = filtered_df[filtered_df['estado'] == filters['estado']]
    
    if filters.get('setor') and filters['setor'] != 'Todos':
        filtered_df = filtered_df[filtered_df['setor'] == filters['setor']]
    
    if filters.get('centro_custo') and filters['centro_custo'] != 'Todos':
        filtered_df = filtered_df[filtered_df['Centro de Custo'] == filters['centro_custo']]
    
    if filters.get('licenca') and filters['licenca'] != 'Todas':
        filtered_df = filtered_df[filtered_df['licenca'] == filters['licenca']]
    
    if filters.get('modalidade') and filters['modalidade'] != 'Todas':
        filtered_df = filtered_df[filtered_df['Modalidade da licença'] == filters['modalidade']]
    
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
        'total_gasto': f"R$ {df['total'].sum():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        'total_usuarios': len(df),
        'total_empresas': df['Empresa'].nunique(),
        'total_licencas': int(df['quantidade de licenças'].sum())
    }
    
    # 1. Gastos por Empresa
    gastos_empresa = df.groupby('Empresa')['total'].sum().sort_values(ascending=False).head(15)
    fig1 = px.bar(x=gastos_empresa.values, y=gastos_empresa.index, orientation='h',
                  labels={'x': 'Gasto Total (R$)', 'y': 'Empresa'},
                  title='💼 Top 15 Empresas por Gasto')
    fig1.update_traces(marker_color='#0078D4')
    graphs['empresas'] = fig1.to_html(full_html=False, div_id="graph1")
    
    # 2. Distribuição por Estado
    estado_counts = df.groupby('estado')['total'].sum()
    fig2 = px.pie(values=estado_counts.values, names=estado_counts.index,
                  title='🗺️ Distribuição por Estado', hole=0.4)
    graphs['estados'] = fig2.to_html(full_html=False, div_id="graph2")
    
    # 3. Top 10 Centros de Custo
    centro_custo = df.groupby('Centro de Custo')['total'].sum().sort_values(ascending=False).head(10)
    fig3 = px.bar(x=centro_custo.index, y=centro_custo.values,
                  labels={'x': 'Centro de Custo', 'y': 'Gasto Total (R$)'},
                  title='🏦 Top 10 Centros de Custo (Maior Gasto)')
    fig3.update_traces(marker_color='#DC3545')
    fig3.update_layout(xaxis_tickangle=-45)
    graphs['centro_custo'] = fig3.to_html(full_html=False, div_id="graph3")
    
    # 4. Licenças Mais Usadas
    licencas_count = df.groupby('licenca')['quantidade de licenças'].sum().sort_values(ascending=False).head(10)
    fig4 = px.bar(x=licencas_count.values, y=licencas_count.index, orientation='h',
                  labels={'x': 'Quantidade', 'y': 'Tipo de Licença'},
                  title='📊 Top 10 Licenças Mais Usadas')
    fig4.update_traces(marker_color='#28A745')
    graphs['licencas'] = fig4.to_html(full_html=False, div_id="graph4")
    
    # 5. Modalidade de Licença
    modalidade = df.groupby('Modalidade da licença')['total'].sum()
    fig5 = px.pie(values=modalidade.values, names=modalidade.index,
                  title='💳 Gastos por Modalidade de Licença', hole=0.3)
    graphs['modalidade'] = fig5.to_html(full_html=False, div_id="graph5")
    
    # 6. Gastos por Setor
    setor = df.groupby('setor')['total'].sum().sort_values(ascending=False).head(15)
    fig6 = px.bar(x=setor.values, y=setor.index, orientation='h',
                  labels={'x': 'Gasto Total (R$)', 'y': 'Setor'},
                  title='🏢 Top 15 Setores por Gasto')
    fig6.update_traces(marker_color='#6F42C1')
    graphs['setor'] = fig6.to_html(full_html=False, div_id="graph6")
    
    # 7. Faturadores
    faturador = df.groupby('faturador')['total'].sum().dropna()
    if len(faturador) > 0:
        fig7 = px.pie(values=faturador.values, names=faturador.index,
                      title='🔄 Distribuição por Fornecedor (Faturador)')
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
    df_contratos = df[df['final contrato'].notna()].copy()
    
    if len(df_contratos) == 0:
        return '<p class="text-muted">Nenhum contrato encontrado com data de vencimento.</p>'
    
    # Agrupar por empresa
    contratos_por_empresa = df_contratos.groupby('Empresa').agg({
        'inicio contrato': 'min',
        'final contrato': 'max',
        'total': 'sum',
        'quantidade de licenças': 'sum'
    }).reset_index()
    
    # Ordenar por data de vencimento (mais próximos primeiro)
    contratos_por_empresa = contratos_por_empresa.sort_values('final contrato')
    
    # Data atual
    hoje = datetime.now()
    sete_dias = hoje + timedelta(days=7)
    
    # Gerar HTML da tabela
    html = '''
    <div class="table-responsive">
        <table class="table table-hover table-sm">
            <thead class="table-dark">
                <tr>
                    <th>Status</th>
                    <th>Empresa</th>
                    <th>Início do Contrato</th>
                    <th>Vencimento</th>
                    <th>Dias Restantes</th>
                    <th>Licenças</th>
                    <th>Valor Total</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for _, row in contratos_por_empresa.iterrows():
        empresa = row['Empresa']
        inicio = row['inicio contrato']
        fim = row['final contrato']
        total = row['total']
        qtd_licencas = row['quantidade de licenças']
        
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
    <title>Dashboard - Licenciamento Microsoft</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .dashboard-header {
            background: linear-gradient(135deg, #0078D4 0%, #0063B1 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .kpi-card {
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            margin-bottom: 20px;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .card-custom {
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .filter-section {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .filter-label {
            font-weight: 600;
            color: #0078D4;
            margin-bottom: 5px;
        }
        .btn-filter {
            background: #0078D4;
            border: none;
            padding: 10px 30px;
            font-weight: 600;
        }
        .btn-filter:hover {
            background: #0063B1;
        }
        .btn-clear {
            background: #6c757d;
            border: none;
            padding: 10px 30px;
            font-weight: 600;
        }
        .btn-clear:hover {
            background: #5a6268;
        }
        .user-card {
            background: #f8f9fa;
            border-left: 4px solid #0078D4;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            transition: all 0.3s;
        }
        .user-card:hover {
            background: #e9ecef;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .badge-licenca {
            cursor: pointer;
            transition: all 0.3s;
        }
        .badge-licenca:hover {
            transform: scale(1.05);
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .table-danger {
            background-color: #f8d7da !important;
            font-weight: 600;
        }
        .table-warning {
            background-color: #fff3cd !important;
            font-weight: 600;
        }
        .table-info {
            background-color: #d1ecf1 !important;
        }
        .table-danger:hover, .table-warning:hover, .table-info:hover {
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <!-- Header -->
        <div class="dashboard-header text-center">
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
                        {{ graphs.contratos | safe }}
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
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Adicionar botões clicáveis para cada licença
        document.addEventListener('DOMContentLoaded', function() {
            // Pegar todas as licenças do gráfico
            const graph4 = document.getElementById('graph4');
            if (graph4) {
                const plotData = graph4.data;
                if (plotData && plotData.length > 0) {
                    const licencas = plotData[0].y;
                    const licencasList = document.getElementById('licencasList');
                    
                    licencasList.innerHTML = '<hr><h6>Clique em uma licença abaixo para ver os usuários:</h6>';
                    licencas.forEach(licenca => {
                        const badge = document.createElement('span');
                        badge.className = 'badge bg-primary badge-licenca me-2 mb-2';
                        badge.style.fontSize = '0.9rem';
                        badge.style.padding = '8px 12px';
                        badge.textContent = licenca;
                        badge.onclick = () => mostrarUsuarios(licenca);
                        licencasList.appendChild(badge);
                    });
                }
            }
        });
        
        function mostrarUsuarios(licenca) {
            const modal = new bootstrap.Modal(document.getElementById('modalUsuarios'));
            document.getElementById('modalTitle').textContent = `👥 Usuários da Licença: ${licenca}`;
            document.getElementById('modalBody').innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Carregando...</span>
                    </div>
                    <p class="mt-2">Carregando usuários...</p>
                </div>
            `;
            modal.show();
            
            // Buscar usuários via API
            fetch(`/api/usuarios/${encodeURIComponent(licenca)}`)
                .then(response => response.json())
                .then(data => {
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
                                            <h6 class="mb-1"><strong>${usuario.colaborador}</strong></h6>
                                            <p class="mb-1 text-muted small">
                                                📧 ${usuario.email || 'Sem email'}<br>
                                                🏢 ${usuario.empresa}<br>
                                                🏭 Setor: ${usuario.setor}<br>
                                                🗺️ Estado: ${usuario.estado}<br>
                                                🏦 Centro de Custo: ${usuario.centro_custo}
                                            </p>
                                        </div>
                                        <div class="col-md-4 text-end">
                                            <p class="mb-1"><strong>Qtd:</strong> ${usuario.quantidade}</p>
                                            <p class="mb-1"><strong>Valor Unit:</strong> R$ ${usuario.valor_unitario?.toFixed(2) || '0.00'}</p>
                                            <p class="mb-0"><strong>Total:</strong> R$ ${usuario.total?.toFixed(2) || '0.00'}</p>
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
        'empresas': sorted(df_original['Empresa'].dropna().unique()),
        'estados': sorted(df_original['estado'].dropna().unique()),
        'setores': sorted(df_original['setor'].dropna().unique()),
        'centros_custo': sorted(df_original['Centro de Custo'].dropna().unique()),
        'licencas': sorted(df_original['licenca'].dropna().unique()),
        'modalidades': sorted(df_original['Modalidade da licença'].dropna().unique())
    }
    
    # Criar gráficos com filtros aplicados
    kpis, graphs = create_graphs(filters)
    update_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    return render_template_string(
        HTML_TEMPLATE, 
        kpis=kpis, 
        graphs=graphs, 
        update_time=update_time,
        filter_options=filter_options,
        current_filters=filters
    )

@app.route('/api/usuarios/<path:licenca>')
def get_usuarios_licenca(licenca):
    """API para retornar usuários de uma licença específica"""
    df = load_data()
    
    # Filtrar por licença
    df_licenca = df[df['licenca'] == licenca]
    
    # Preparar dados dos usuários
    usuarios = []
    for _, row in df_licenca.iterrows():
        usuarios.append({
            'colaborador': row['Nome do colaborador'] if pd.notna(row['Nome do colaborador']) else 'Sem nome',
            'email': row['e-mail'] if pd.notna(row['e-mail']) else '',
            'empresa': row['Empresa'] if pd.notna(row['Empresa']) else '',
            'setor': row['setor'] if pd.notna(row['setor']) else '',
            'estado': row['estado'] if pd.notna(row['estado']) else '',
            'centro_custo': row['Centro de Custo'] if pd.notna(row['Centro de Custo']) else '',
            'quantidade': float(row['quantidade de licenças']) if pd.notna(row['quantidade de licenças']) else 0,
            'valor_unitario': float(row['valor unitario']) if pd.notna(row['valor unitario']) else 0,
            'total': float(row['total']) if pd.notna(row['total']) else 0
        })
    
    return jsonify({
        'licenca': licenca,
        'total_usuarios': len(usuarios),
        'usuarios': usuarios
    })

if __name__ == '__main__':
    import os
    
    print("\n" + "="*80)
    print("🚀 Dashboard de Licenciamento Microsoft")
    print("="*80)
    print("\n📊 Dashboard iniciando...")
    
    # Verificar se está rodando em Docker
    in_docker = os.path.exists('/.dockerenv')
    
    if in_docker:
        print("🐳 Rodando em Docker")
        print("🌐 Acesse: http://localhost:5000 (do seu navegador)")
    else:
        print("💻 Rodando localmente")
        print("🌐 Acesse: http://127.0.0.1:5000")
    
    print("\n💡 Dica: Clique em 'Atualizar' após modificar a planilha ou pressione F5")
    print("💡 Clique em uma licença para ver todos os usuários!")
    print("💡 Para parar: Pressione Ctrl+C")
    print("="*80 + "\n")
    
    # Em Docker, bind em 0.0.0.0 para aceitar conexões externas
    host = '0.0.0.0' if in_docker else '127.0.0.1'
    
    app.run(debug=False, port=5000, host=host)
