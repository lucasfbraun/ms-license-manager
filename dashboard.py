import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime
import os

# ========================================
# CONFIGURAÇÕES E CARREGAMENTO DE DADOS
# ========================================

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

# ========================================
# CRIAÇÃO DO DASHBOARD
# ========================================

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard - Licenciamento Microsoft"

# ========================================
# LAYOUT
# ========================================

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("📊 Dashboard de Licenciamento Microsoft", 
                   className="text-center mb-4 mt-4",
                   style={'color': '#0078D4', 'font-weight': 'bold'}),
        ])
    ]),
    
    # Botão de atualização
    dbc.Row([
        dbc.Col([
            dbc.Button("🔄 Atualizar Dados", id="refresh-button", color="primary", className="mb-3"),
            html.Span(id="last-update", className="ms-3 text-muted")
        ])
    ]),
    
    # Cards com KPIs
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("💰 Gasto Total", className="card-title"),
                    html.H2(id="total-gasto", className="text-success"),
                    html.P("Total investido em licenças", className="text-muted")
                ])
            ], className="mb-3 shadow-sm")
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("👥 Total de Usuários", className="card-title"),
                    html.H2(id="total-usuarios", className="text-primary"),
                    html.P("Usuários com licenças", className="text-muted")
                ])
            ], className="mb-3 shadow-sm")
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("🏢 Empresas", className="card-title"),
                    html.H2(id="total-empresas", className="text-info"),
                    html.P("Empresas cadastradas", className="text-muted")
                ])
            ], className="mb-3 shadow-sm")
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📋 Licenças", className="card-title"),
                    html.H2(id="total-licencas", className="text-warning"),
                    html.P("Total de licenças ativas", className="text-muted")
                ])
            ], className="mb-3 shadow-sm")
        ], md=3),
    ]),
    
    # Gráficos principais
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("💼 Gastos por Empresa", className="card-title"),
                    dcc.Graph(id="graph-empresa")
                ])
            ], className="mb-3 shadow-sm")
        ], md=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("🗺️ Distribuição por Estado", className="card-title"),
                    dcc.Graph(id="graph-estado")
                ])
            ], className="mb-3 shadow-sm")
        ], md=6),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("🏦 Top 10 Centros de Custo (Maior Gasto)", className="card-title"),
                    dcc.Graph(id="graph-centro-custo")
                ])
            ], className="mb-3 shadow-sm")
        ], md=12),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📊 Distribuição de Licenças por Tipo", className="card-title"),
                    dcc.Graph(id="graph-licencas")
                ])
            ], className="mb-3 shadow-sm")
        ], md=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("💳 Gastos por Modalidade de Licença", className="card-title"),
                    dcc.Graph(id="graph-modalidade")
                ])
            ], className="mb-3 shadow-sm")
        ], md=6),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("🏢 Gastos por Setor", className="card-title"),
                    dcc.Graph(id="graph-setor")
                ])
            ], className="mb-3 shadow-sm")
        ], md=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("🔄 Fornecedores (Faturadores)", className="card-title"),
                    dcc.Graph(id="graph-faturador")
                ])
            ], className="mb-3 shadow-sm")
        ], md=6),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📅 Contratos Vencendo nos Próximos 90 Dias", className="card-title"),
                    html.Div(id="contratos-vencendo")
                ])
            ], className="mb-3 shadow-sm border-warning")
        ], md=12),
    ]),
    
    # Tabela detalhada
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📋 Detalhamento Completo", className="card-title"),
                    html.Div(id="tabela-detalhada")
                ])
            ], className="mb-3 shadow-sm")
        ], md=12),
    ]),
    
    # Storage para armazenar timestamp
    dcc.Store(id='data-store'),
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)  # Atualiza a cada 1 minuto
    
], fluid=True, style={'backgroundColor': '#f8f9fa'})

# ========================================
# CALLBACKS
# ========================================

@app.callback(
    [Output('data-store', 'data'),
     Output('last-update', 'children')],
    [Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_data(n_clicks, n_intervals):
    """Atualiza os dados quando o botão é clicado ou automaticamente"""
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return {'timestamp': now}, f"Última atualização: {now}"

@app.callback(
    [Output('total-gasto', 'children'),
     Output('total-usuarios', 'children'),
     Output('total-empresas', 'children'),
     Output('total-licencas', 'children'),
     Output('graph-empresa', 'figure'),
     Output('graph-estado', 'figure'),
     Output('graph-centro-custo', 'figure'),
     Output('graph-licencas', 'figure'),
     Output('graph-modalidade', 'figure'),
     Output('graph-setor', 'figure'),
     Output('graph-faturador', 'figure'),
     Output('contratos-vencendo', 'children'),
     Output('tabela-detalhada', 'children')],
    [Input('data-store', 'data')]
)
def update_graphs(data):
    """Atualiza todos os gráficos e KPIs"""
    df = load_data()
    
    # KPIs
    total_gasto = f"R$ {df['total'].sum():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    total_usuarios = f"{len(df)}"
    total_empresas = f"{df['Empresa'].nunique()}"
    total_licencas = f"{df['quantidade de licenças'].sum():.0f}"
    
    # Gráfico 1: Gastos por Empresa
    gastos_empresa = df.groupby('Empresa')['total'].sum().sort_values(ascending=True).tail(15)
    fig_empresa = px.bar(
        x=gastos_empresa.values,
        y=gastos_empresa.index,
        orientation='h',
        title="",
        labels={'x': 'Gasto Total (R$)', 'y': 'Empresa'},
        color=gastos_empresa.values,
        color_continuous_scale='Blues'
    )
    fig_empresa.update_layout(showlegend=False, height=400)
    
    # Gráfico 2: Distribuição por Estado
    estado_counts = df.groupby('estado').agg({
        'total': 'sum',
        'quantidade de licenças': 'sum'
    }).reset_index()
    fig_estado = px.pie(
        estado_counts,
        values='total',
        names='estado',
        title="",
        hole=0.4
    )
    fig_estado.update_layout(height=400)
    
    # Gráfico 3: Top 10 Centros de Custo
    centro_custo = df.groupby('Centro de Custo')['total'].sum().sort_values(ascending=False).head(10)
    fig_centro = px.bar(
        x=centro_custo.index,
        y=centro_custo.values,
        title="",
        labels={'x': 'Centro de Custo', 'y': 'Gasto Total (R$)'},
        color=centro_custo.values,
        color_continuous_scale='Reds'
    )
    fig_centro.update_layout(showlegend=False, height=400, xaxis_tickangle=-45)
    
    # Gráfico 4: Distribuição de Licenças
    licencas_count = df.groupby('licenca')['quantidade de licenças'].sum().sort_values(ascending=False).head(10)
    fig_licencas = px.bar(
        x=licencas_count.values,
        y=licencas_count.index,
        orientation='h',
        title="",
        labels={'x': 'Quantidade', 'y': 'Tipo de Licença'},
        color=licencas_count.values,
        color_continuous_scale='Greens'
    )
    fig_licencas.update_layout(showlegend=False, height=400)
    
    # Gráfico 5: Modalidade de Licença
    modalidade = df.groupby('Modalidade da licença')['total'].sum()
    fig_modalidade = px.pie(
        values=modalidade.values,
        names=modalidade.index,
        title="",
        hole=0.3
    )
    fig_modalidade.update_layout(height=400)
    
    # Gráfico 6: Gastos por Setor
    setor = df.groupby('setor')['total'].sum().sort_values(ascending=True).tail(15)
    fig_setor = px.bar(
        x=setor.values,
        y=setor.index,
        orientation='h',
        title="",
        labels={'x': 'Gasto Total (R$)', 'y': 'Setor'},
        color=setor.values,
        color_continuous_scale='Purples'
    )
    fig_setor.update_layout(showlegend=False, height=400)
    
    # Gráfico 7: Faturadores
    faturador = df.groupby('faturador')['total'].sum().dropna()
    fig_faturador = px.pie(
        values=faturador.values,
        names=faturador.index,
        title=""
    )
    fig_faturador.update_layout(height=400)
    
    # Contratos Vencendo
    hoje = pd.Timestamp.now()
    df_vencendo = df[df['final contrato'].notna()].copy()
    df_vencendo = df_vencendo[df_vencendo['final contrato'] <= hoje + pd.Timedelta(days=90)]
    df_vencendo = df_vencendo[df_vencendo['final contrato'] >= hoje]
    df_vencendo = df_vencendo.sort_values('final contrato')
    
    if len(df_vencendo) > 0:
        contratos_html = dbc.Table.from_dataframe(
            df_vencendo[['Empresa', 'Nome do colaborador', 'licenca', 'final contrato', 'total']].head(10),
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            size='sm'
        )
    else:
        contratos_html = html.P("✅ Nenhum contrato vencendo nos próximos 90 dias", className="text-success")
    
    # Tabela Detalhada
    tabela_df = df[['Empresa', 'Nome do colaborador', 'licenca', 'Centro de Custo', 'estado', 'total']].head(50)
    tabela_html = dbc.Table.from_dataframe(
        tabela_df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm'
    )
    
    return (
        total_gasto, total_usuarios, total_empresas, total_licencas,
        fig_empresa, fig_estado, fig_centro, fig_licencas, 
        fig_modalidade, fig_setor, fig_faturador,
        contratos_html, tabela_html
    )

# ========================================
# EXECUTAR APLICAÇÃO
# ========================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 Dashboard de Licenciamento Microsoft")
    print("="*80)
    print("\n📊 Dashboard iniciando...")
    print("🌐 Acesse: http://127.0.0.1:8050")
    print("\n💡 Dica: Clique em 'Atualizar Dados' após modificar a planilha")
    print("="*80 + "\n")
    
    app.run(debug=True, port=8050)
