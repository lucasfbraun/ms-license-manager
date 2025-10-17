from flask import Flask, render_template_string, request, jsonify, Response
import pandas as pd
import numpy as np
import math
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
from urllib.parse import quote
import re
from io import StringIO
import csv

app = Flask(__name__)

# Configurar JSON encoder para não permitir NaN
app.json.ensure_ascii = False
app.json.sort_keys = False

# Custom JSON encoder que converte NaN para null
from flask.json.provider import DefaultJSONProvider

class SafeJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
        return super().default(obj)

app.json = SafeJSONProvider(app)

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


@app.route('/api/export_selected', methods=['POST'])
def api_export_selected():
    try:
        payload = request.get_json(force=True)
        emails = payload.get('emails') if payload else None
        if not emails or not isinstance(emails, list):
            return jsonify({'error':'emails list required'}), 400

        df = load_data()
        # normalize email column name variations
        email_col = None
        for c in df.columns:
            if c.lower() in ('email','e-mail'):
                email_col = c
                break
        if email_col is None:
            return jsonify({'error':'Email column not found in data'}), 500

        # filter rows where email in selected emails
        sel_df = df[df[email_col].isin(emails)].copy()

        if sel_df.empty:
            # return empty CSV
            si = StringIO()
            writer = csv.writer(si)
            writer.writerow(['Empresa','Colaborador','Email','Licenca','Centro de Custo','Valor por Centro de Custo','% por Centro de Custo'])
            output = si.getvalue()
            return Response(output, mimetype='text/csv', headers={'X-Filename':'export_selected.csv'})

        # compute per-centro totals among selected rows
        # assume valorTotalLicenca (numeric) is the amount per row to be allocated
        if 'valorTotalLicenca' not in sel_df.columns:
            sel_df['valorTotalLicenca'] = pd.to_numeric(sel_df.get('valorTotalLicenca', pd.Series([0]*len(sel_df))), errors='coerce').fillna(0)

        # sum total per Centro de Custo across selected rows
        centro_sum = sel_df.groupby('Centro de Custo')['valorTotalLicenca'].sum().to_dict()

        # For each selected user row, allocate its valorTotalLicenca across centros proportionally to centro_sum
        # The user's share for a centro = (user.valorTotalLicenca / total_selected_valor) * centro_sum[centro]
        total_selected_valor = sel_df['valorTotalLicenca'].sum()
        # If total_selected_valor is 0, percent will be 0

        # Build CSV
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(['Empresa','Colaborador','Email','Licenca','Centro de Custo','Valor por Centro de Custo','% por Centro de Custo'])

        for idx, row in sel_df.iterrows():
            empresa = row.get('empresa','')
            colaborador = row.get('Colaborador','') if 'Colaborador' in row else row.get('colaborador','')
            email = row.get(email_col,'')
            licenca = row.get('licenca','')
            user_val = float(row.get('valorTotalLicenca') or 0)

            # allocate across centros; if total_selected_valor == 0 then percent 0 and allocated 0
            for centro, centro_total in centro_sum.items():
                if total_selected_valor and centro_total:
                    allocated = (user_val / total_selected_valor) * centro_total
                    pct = (allocated / centro_total) * 100 if centro_total else 0
                else:
                    allocated = 0.0
                    pct = 0.0

                writer.writerow([
                    empresa,
                    colaborador,
                    email,
                    licenca,
                    centro,
                    f"{allocated:.2f}",
                    f"{pct:.2f}"
                ])

        output = si.getvalue()
        return Response(output, mimetype='text/csv', headers={'X-Filename':'export_selected.csv'})
    except Exception as e:
        app.logger.exception('Erro gerando CSV de export_selected')
        return jsonify({'error': str(e)}), 500

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
    <div class="mb-3 d-flex justify-content-between align-items-center">
        <div>
            <button id="export_rateio_btn" class="btn btn-success btn-sm" disabled>
                📥 Exportar Rateio CSV (contratos selecionados)
            </button>
            <span class="ms-3 text-muted small" id="sel_count">(0 contratos selecionados)</span>
        </div>
        <div>
            <button id="clear_selection" class="btn btn-outline-secondary btn-sm">Limpar seleção</button>
        </div>
    </div>
    
    <div class="table-responsive">
        <table id="graph_contratos" class="table table-hover table-sm">
            <thead class="table-dark">
                <tr>
                    <th style="width: 70px; text-align: center;">
                        <div style="font-size: 0.75rem; margin-bottom: 5px; color: var(--title-color);">Selecionar</div>
                        <input type="checkbox" id="checkAllContratos" class="form-check-input">
                    </th>
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
                    <td style="text-align: center;">
                        <input type="checkbox" class="contrato-checkbox form-check-input" 
                               data-empresa="{empresa}" 
                               data-licenca="{licenca}" 
                               data-modalidade="{modalidade}">
                    </td>
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
    
    <script>
    (function(){
        const checkAll = document.getElementById('checkAllContratos');
    // Handler para abrir a modal com todos os usuários ao clicar no KPI
    (function(){
        function renderUsersTable(usuarios, container, page=1, pageSize=25){
            const start = (page-1)*pageSize;
            const end = start + pageSize;
            const pageItems = usuarios.slice(start, end);

            let html = '<div class="table-responsive"><table class="table table-sm table-striped"><thead><tr>';
            const keys = Object.keys(usuarios[0] || {});
            for(const k of keys){ html += `<th>${k}</th>` }
            html += '</tr></thead><tbody>';
            for(const u of pageItems){
                html += '<tr>';
                for(const k of keys){ html += `<td>${u[k]===null||u[k]===undefined?'':u[k]}</td>` }
                html += '</tr>';
            }
            html += `</tbody></table></div>`;

            // paginação simples
            const totalPages = Math.max(1, Math.ceil(usuarios.length / pageSize));
            html += '<nav><ul class="pagination pagination-sm">';
            for(let p=1;p<=totalPages;p++){
                html += `<li class="page-item ${p===page?'active':''}"><a href="#" class="page-link" data-page="${p}">${p}</a></li>`;
            }
            html += '</ul></nav>';

            container.innerHTML = html;
            // attach page click
            container.querySelectorAll('.page-link').forEach(a=>{
                a.addEventListener('click', function(e){
                    e.preventDefault();
                    const p = parseInt(this.getAttribute('data-page'))||1;
                    renderUsersTable(usuarios, container, p, pageSize);
                })
            })
        }

        const kpi = document.getElementById('kpi-total-usuarios');
        if(kpi){
            kpi.style.cursor = 'pointer';
            kpi.addEventListener('click', function(){
                const modal = document.getElementById('modalUsuarios');
                const modalBody = modal.querySelector('.modal-body');
                modal.querySelector('.modal-title').textContent = 'Todos os Usuários';
                modalBody.innerHTML = '<p>Carregando usuários...</p>';
                // abrir modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();

                fetch('/api/usuarios').then(r=>r.json()).then(data=>{
                    const usuarios = data.usuarios || [];
                    if(usuarios.length===0){ modalBody.innerHTML = '<p>Nenhum usuário encontrado.</p>'; return; }
                    renderUsersTable(usuarios, modalBody, 1, 25);
                }).catch(err=>{
                    console.error('Erro ao carregar todos os usuários', err);
                    modalBody.innerHTML = '<div class="text-danger">Erro ao carregar usuários. Veja console.</div>';
                })
            })
        }
    })();
        const exportBtn = document.getElementById('export_rateio_btn');
        const clearBtn = document.getElementById('clear_selection');
        const selCountEl = document.getElementById('sel_count');

        function updateState() {
            const checked = Array.from(document.querySelectorAll('.contrato-checkbox:checked'));
            const count = checked.length;
            selCountEl.textContent = '(' + count + ' contratos selecionados)';
            exportBtn.disabled = count === 0;
            const all = document.querySelectorAll('.contrato-checkbox');
            if (all.length > 0 && checkAll) {
                checkAll.checked = checked.length === all.length;
            }
        }

        document.addEventListener('change', function(e){
            if (e.target && e.target.classList && e.target.classList.contains('contrato-checkbox')) {
                updateState();
            }
            if (e.target && e.target.id === 'checkAllContratos') {
                const checked = e.target.checked;
                document.querySelectorAll('.contrato-checkbox').forEach(function(cb){ cb.checked = checked; });
                updateState();
            }
        });

        if (clearBtn) {
            clearBtn.addEventListener('click', function(){
                document.querySelectorAll('.contrato-checkbox').forEach(function(cb){ cb.checked = false; });
                if (checkAll) checkAll.checked = false;
                updateState();
            });
        }

        function downloadBlob(blob, filename) {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        }

        if (exportBtn) {
            exportBtn.addEventListener('click', function(){
                const checked = Array.from(document.querySelectorAll('.contrato-checkbox:checked'));
                if (checked.length === 0) {
                    alert('Selecione pelo menos um contrato para exportar.');
                    return;
                }
                const contracts = checked.map(function(cb){
                    return {
                        empresa: cb.getAttribute('data-empresa'),
                        licenca: cb.getAttribute('data-licenca'),
                        modalidade: cb.getAttribute('data-modalidade')
                    };
                });
                exportBtn.disabled = true;
                exportBtn.textContent = 'Gerando CSV...';
                fetch('/api/rateio_contratos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ contracts: contracts })
                }).then(function(res){
                    if (!res.ok) throw new Error('Falha na geração do CSV');
                    const disposition = res.headers.get('Content-Disposition') || '';
                    const filenameMatch = /filename="(.+)"/.exec(disposition);
                    const filename = filenameMatch ? filenameMatch[1] : 'rateio_consolidado.csv';
                    return res.blob().then(function(blob){ return { blob: blob, filename: filename }; });
                }).then(function(data){
                    downloadBlob(data.blob, data.filename);
                }).catch(function(err){
                    console.error(err);
                    alert('Erro ao gerar o CSV: ' + err.message);
                }).finally(function(){
                    exportBtn.disabled = false;
                    exportBtn.textContent = '📥 Exportar Rateio CSV (contratos selecionados)';
                    updateState();
                });
            });
        }

        updateState();
    })();
    </script>
    <script>
    // Inline All Users list: fetch, sort by creation date desc, search, and render
    (function(){
        const container = document.getElementById('allusers-container');
        const listEl = document.getElementById('allusers-list');
        const loadingEl = document.getElementById('allusers-loading');
        const input = document.getElementById('allusers-search');
        const refreshBtn = document.getElementById('allusers-refresh');
        const exportBtn = document.getElementById('allusers-export');

        if(!container || !listEl || !loadingEl) return;

        let allUsers = [];

        function parseDateSafe(val){
            if(!val) return null;
            // try ISO parse
            const d = new Date(val);
            if(!isNaN(d)) return d;
            // try dd/mm/yyyy
            const parts = String(val).split('/');
            if(parts.length===3){
                const dd = parts[0], mm = parts[1], yyyy = parts[2];
                const dx = new Date(`${yyyy}-${mm}-${dd}`);
                if(!isNaN(dx)) return dx;
            }
            return null;
        }

        function renderRows(arr){
            if(!Array.isArray(arr)) arr = [];
            if(arr.length===0){
                listEl.innerHTML = '<div class="text-muted p-3">Nenhum usuário encontrado.</div>';
                listEl.style.display = '';
                return;
            }

            const html = arr.map(u=>{
                const created = u['Data de Criação'] || u['DataCriacaoEmail'] || u['DataCriacaoFormatada'] || '';
                const createdFmt = created ? String(created).replace('T00:00:00','') : '';
                const centro = u['Centro de Custo'] || '';
                const empresa = u['Empresa'] || '';
                const fmtNumber = (n)=> Number(n||0).toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});
                const totalNum = u['Total'] ?? u['total'] ?? 0;
                const valorTotalStr = u['Valor Total'] || u['ValorTotal'] || (totalNum ? ('R$ ' + fmtNumber(totalNum)) : 'R$ 0,00');
                // Surround each user with a checkbox for selection
                return `
                    <div class="user-card mb-2 p-2 border rounded d-flex align-items-center">
                        <div style="width:36px; flex:0 0 36px;">
                            <input type="checkbox" class="user-select-checkbox form-check-input" data-email="${(u['Email']||'').replace(/"/g,'')}">
                        </div>
                        <div style="flex:1;">
                            <strong>${u['Colaborador'] || ''}</strong><br>
                            <small class="text-muted">${u['Email'] || ''} • ${empresa} • ${centro}</small>
                        </div>
                        <div style="width:200px; text-align:right;">
                            <p class="mb-1"><small class="text-muted">${createdFmt}</small></p>
                            <p class="mb-1"><strong>Qtd:</strong> ${u['Quantidade'] ?? ''}</p>
                            <p class="mb-1"><strong>Valor Unit:</strong> ${u['Valor Unitário']? 'R$ ' + Number(u['Valor Unitário']).toLocaleString('pt-BR', {minimumFractionDigits:2}): ''}</p>
                            <p class="mb-0"><strong>Valor Total:</strong> ${valorTotalStr}</p>
                        </div>
                    </div>`;
            }).join('');

            listEl.innerHTML = html;
            listEl.style.display = '';
        }

        function applySearchAndRender(){
            const term = (input && input.value || '').toLowerCase();
            let filtered = allUsers.filter(u => {
                const txt = [u['Colaborador'], u['Email'], u['Empresa'], u['Centro de Custo']].map(x => (x||'').toString().toLowerCase()).join(' ');
                return txt.includes(term);
            });
            renderRows(filtered);
        }

        function fetchAndRender(){
            loadingEl.style.display = '';
            listEl.style.display = 'none';
            fetch('/api/usuarios').then(r=>{ if(!r.ok) throw new Error('HTTP '+r.status); return r.json(); }).then(data=>{
                const users = (data && data.usuarios) ? data.usuarios : [];
                // normalize dates
                users.forEach(u=>{
                    const candidates = ['Data de Criação','DataCriacaoEmail','DataCriacaoFormatada'];
                    let found = null;
                    for(const c of candidates){ if(u[c]) { found = u[c]; break; } }
                    u.__created = parseDateSafe(found);
                });

                // sort desc by __created (nulls last)
                users.sort((a,b)=>{
                    const da = a.__created, db = b.__created;
                    if(da && db) return db - da;
                    if(da && !db) return -1;
                    if(!da && db) return 1;
                    return 0;
                });

                allUsers = users;
                loadingEl.style.display = 'none';
                applySearchAndRender();
                // attach change handlers to checkboxes after render
                setTimeout(()=>{
                    const allCheckboxes = Array.from(document.querySelectorAll('.user-select-checkbox'));
                    allCheckboxes.forEach(cb=>{
                        cb.addEventListener('change', ()=>{
                            const any = allCheckboxes.some(x=>x.checked);
                            if(exportBtn) exportBtn.disabled = !any;
                            // sync select-all checkbox
                            const selAll = document.getElementById('allusers-select-all');
                            if(selAll) selAll.checked = allCheckboxes.length>0 && allCheckboxes.every(x=>x.checked);
                        });
                    });

                    // select-all behavior
                    const selAll = document.getElementById('allusers-select-all');
                    if(selAll){
                        selAll.addEventListener('change', function(){
                            const on = !!this.checked;
                            document.querySelectorAll('.user-select-checkbox').forEach(x=>{ x.checked = on; });
                            if(exportBtn) exportBtn.disabled = !on;
                        });
                    }
                }, 50);
            }).catch(err=>{
                console.error('Erro fetching all users inline:', err);
                loadingEl.innerHTML = `<div class="text-danger p-3">Erro ao carregar usuários: ${err.message}</div>`;
            });
        }

        if(input) input.addEventListener('input', applySearchAndRender);
        if(refreshBtn) refreshBtn.addEventListener('click', fetchAndRender);
        if(exportBtn) exportBtn.addEventListener('click', function(){
            // collect selected users
            const selected = Array.from(document.querySelectorAll('.user-select-checkbox')).filter(x=>x.checked).map(x=>x.getAttribute('data-email'));
            if(selected.length===0){ alert('Selecione pelo menos um usuário para exportar.'); return; }

            // prepare payload: send list of emails to server which will compute per-centro totals
            fetch('/api/export_selected', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({ emails: selected })
            }).then(r=>{
                if(!r.ok) throw new Error('HTTP ' + r.status);
                return r.blob().then(b=>({ blob: b, filename: (r.headers.get('X-Filename')||'export_selected.csv') }));
            }).then(data=>{
                const url = URL.createObjectURL(data.blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = data.filename;
                document.body.appendChild(a);
                a.click();
                a.remove();
                URL.revokeObjectURL(url);
            }).catch(err=>{ console.error('Erro export:', err); alert('Erro ao exportar: '+err.message); });
        });

        // initial load
        fetchAndRender();
    })();
    </script>
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
        
        /* Estilo personalizado para checkboxes - Paleta de cores do dashboard */
        .contrato-checkbox.form-check-input,
        #checkAllContratos.form-check-input {
            width: 20px;
            height: 20px;
            cursor: pointer;
            border: 2px solid var(--primary);
            border-radius: 4px;
            transition: all 0.2s ease;
            background-color: #FFFFFF;
            --bs-form-check-bg-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3e%3cpath fill='none' stroke='%23FFFFFF' stroke-linecap='round' stroke-linejoin='round' stroke-width='3' d='m6 10 3 3 6-6'/%3e%3c/svg%3e");
        }
        
        .contrato-checkbox.form-check-input:hover,
        #checkAllContratos.form-check-input:hover {
            border-color: var(--accent-light);
            box-shadow: 0 0 8px rgba(96, 147, 105, 0.3);
        }
        
        .contrato-checkbox.form-check-input:checked,
        #checkAllContratos.form-check-input:checked {
            background-color: #609369 !important;
            border-color: #609369 !important;
            background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3e%3cpath fill='none' stroke='%23FFFFFF' stroke-linecap='round' stroke-linejoin='round' stroke-width='3' d='m6 10 3 3 6-6'/%3e%3c/svg%3e") !important;
        }
        
        .contrato-checkbox.form-check-input:checked:hover,
        #checkAllContratos.form-check-input:checked:hover {
            background-color: #7FB88A !important;
            border-color: #7FB88A !important;
        }
        
        .contrato-checkbox.form-check-input:focus,
        #checkAllContratos.form-check-input:focus {
            border-color: #609369 !important;
            box-shadow: 0 0 0 0.25rem rgba(96, 147, 105, 0.25) !important;
            outline: none !important;
        }
        
        .contrato-checkbox.form-check-input:active,
        #checkAllContratos.form-check-input:active {
            border-color: #609369 !important;
            background-color: #7FB88A !important;
        }
        
        .contrato-checkbox.form-check-input:checked:focus,
        #checkAllContratos.form-check-input:checked:focus {
            background-color: #609369 !important;
            border-color: #609369 !important;
            box-shadow: 0 0 0 0.25rem rgba(96, 147, 105, 0.25) !important;
        }
        
        .contrato-checkbox.form-check-input:checked:active,
        #checkAllContratos.form-check-input:checked:active {
            background-color: #7FB88A !important;
            border-color: #7FB88A !important;
        }
        
        .table {
            color: #333333;
            background-color: #FFFFFF;
        }
        
        .table-hover tbody tr:hover {
            background-color: rgba(96, 147, 105, 0.1) !important;
        }

        /* Chips (Filtros rápidos) usando a paleta */
        #chips-empresa .btn,
        #chips-setor .btn,
        #chips-estado .btn {
            border-radius: 999px;
            padding: 4px 10px;
            font-weight: 600;
        }

        /* Estado inativo (outline) no escopo dos chips */
        #chips-empresa .btn-outline-primary,
        #chips-setor .btn-outline-primary,
        #chips-estado .btn-outline-primary {
            color: var(--primary) !important;
            border-color: var(--primary) !important;
            background-color: #FFFFFF !important;
        }
        #chips-empresa .btn-outline-primary:hover,
        #chips-setor .btn-outline-primary:hover,
        #chips-estado .btn-outline-primary:hover {
            color: #FFFFFF !important;
            background-color: var(--primary) !important;
            border-color: var(--primary) !important;
        }

        /* Ativo (filled) no escopo dos chips */
        #chips-empresa .btn-primary,
        #chips-setor .btn-primary,
        #chips-estado .btn-primary {
            color: #FFFFFF !important;
            background-color: var(--primary) !important;
            border-color: var(--primary) !important;
            box-shadow: 0 2px 6px rgba(96, 147, 105, 0.3);
        }
        #chips-empresa .btn-primary:hover,
        #chips-setor .btn-primary:hover,
        #chips-estado .btn-primary:hover {
            filter: brightness(0.95);
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
                        <h2 id="kpi-total-usuarios">{{ kpis.total_usuarios }}</h2>
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
        
        <!-- Card: Todos os Usuários (inline) -->
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card card-custom">
                    <div class="card-body">
                        <h5 class="card-title">👥 Todos os Usuários (Lista)</h5>
                        <p class="text-muted">Lista inline com pesquisa e rolagem, ordenada por Data de Criação (mais recente primeiro).</p>
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <input id="allusers-search" type="text" class="form-control form-control-sm" placeholder="Pesquisar usuário, email, empresa, centro de custo...">
                            </div>
                            <div class="col-md-6 text-end">
                                <div class="d-inline-flex align-items-center">
                                    <input id="allusers-select-all" type="checkbox" class="form-check-input me-2" title="Selecionar todos">
                                    <button id="allusers-refresh" class="btn btn-sm btn-outline-primary me-2">Atualizar</button>
                                    <button id="allusers-export" class="btn btn-sm btn-success" disabled>📥 Exportar CSV</button>
                                </div>
                            </div>
                        </div>

                        <div id="allusers-container" style="max-height:600px; overflow-y:auto;">
                            <div class="text-center py-4" id="allusers-loading">
                                <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Carregando...</span></div>
                            </div>
                            <div id="allusers-list" style="display:none;"></div>
                        </div>
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
        console.log('=== INICIO mostrarUsuarios ===');
        console.log('Licença recebida:', licenca);
        console.log('Tipo:', typeof licenca);
        
        const modalEl = document.getElementById('modalUsuarios');
        const modalBody = document.getElementById('modalBody');
        const modalTitle = document.getElementById('modalTitle');
        
        console.log('Elementos encontrados:', {
            modalEl: !!modalEl,
            modalBody: !!modalBody,
            modalTitle: !!modalTitle
        });
        
        if (!modalEl || !modalBody || !modalTitle) {
            console.error('ERRO: Elementos do modal não encontrados!');
            alert('Erro ao abrir modal. Por favor, recarregue a página.');
            return;
        }
        
        // Atualizar título
        modalTitle.textContent = `👥 Usuários da Licença: ${licenca}`;
        console.log('Título atualizado');
        
        // Mostrar loading
        modalBody.innerHTML = `
            <div class="text-center p-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
                <p class="mt-3">Carregando usuários...</p>
            </div>
        `;
        console.log('Loading exibido');
        
        // Abrir modal
        try {
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
            console.log('Modal aberto');
        } catch(e) {
            console.error('Erro ao abrir modal:', e);
        }
        
        // Buscar dados
        const url = `/api/usuarios/${encodeURIComponent(licenca)}`;
        console.log('URL da API:', url);
        
        fetch(url)
            .then(response => {
                console.log('=== RESPONSE ===');
                console.log('Status:', response.status);
                console.log('OK:', response.ok);
                console.log('StatusText:', response.statusText);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('=== DADOS RECEBIDOS ===');
                console.log('Data completo:', data);
                console.log('Tipo de data:', typeof data);
                console.log('Data.usuarios existe:', 'usuarios' in data);
                console.log('Data.usuarios é array:', Array.isArray(data.usuarios));
                console.log('Quantidade de usuários:', data.usuarios ? data.usuarios.length : 0);
                
                if (!data || typeof data !== 'object') {
                    throw new Error('Resposta inválida da API');
                }
                
                const hasUsers = Array.isArray(data.usuarios) && data.usuarios.length > 0;
                const usuariosData = hasUsers ? data.usuarios : [];
                
                console.log('hasUsers:', hasUsers);
                console.log('usuariosData length:', usuariosData.length);
                
                if (!hasUsers) {
                    modalBody.innerHTML = `
                        <div class="alert alert-info">
                            <strong>Total de usuários: 0</strong><br>
                            Nenhum usuário encontrado para esta licença.
                        </div>
                    `;
                    return;
                }
                
                // Derivar chips (Empresa, Setor, Estado)
                const uniq = (arr) => Array.from(new Set(arr.filter(v => v != null && v !== ''))).sort();
                const empresas = uniq(usuariosData.map(u => u['Empresa']));
                const setores = uniq(usuariosData.map(u => u['Setor']));
                const estados = uniq(usuariosData.map(u => u['Estado']));
                
                // Estado do filtro e paginação
                let filtroTexto = '';
                let filtroEmpresa = null;
                let filtroSetor = null;
                let filtroEstado = null;
                let pagina = 1;
                const porPagina = 10;

                // Construir HTML
                let html = `
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <div class="alert alert-info mb-0">
                            <strong>Total de usuários com esta licença: ${data.total_usuarios}</strong>
                        </div>
                        <div class="input-group" style="max-width: 360px;">
                            <input type="text" id="usuarios-search" class="form-control form-control-sm" placeholder="Pesquisar usuário, email, empresa...">
                            <button class="btn btn-outline-secondary btn-sm" id="usuarios-clear" type="button">Limpar</button>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <div class="d-flex flex-wrap gap-2 align-items-center">
                            <span class="text-muted small me-2">Filtros rápidos:</span>
                            <div id="chips-empresa" class="d-flex flex-wrap gap-2"></div>
                            <div id="chips-setor" class="d-flex flex-wrap gap-2"></div>
                            <div id="chips-estado" class="d-flex flex-wrap gap-2"></div>
                            <button class="btn btn-sm btn-outline-secondary" id="chips-clear">Limpar filtros</button>
                        </div>
                    </div>
                    <div id="usuariosList"></div>
                    <div id="usuariosPagination" class="d-flex justify-content-between align-items-center mt-3"></div>
                `;

                console.log('=== CONSTRUINDO HTML ===');
                console.log('HTML length:', html.length);
                
                modalBody.innerHTML = html;
                console.log('HTML inserido no modalBody');

                // Filtro + chips + paginação
                const input = document.getElementById('usuarios-search');
                const clearBtn = document.getElementById('usuarios-clear');
                const chipsEmpresa = document.getElementById('chips-empresa');
                const chipsSetor = document.getElementById('chips-setor');
                const chipsEstado = document.getElementById('chips-estado');
                const chipsClear = document.getElementById('chips-clear');
                const listEl = document.getElementById('usuariosList');
                const pagerEl = document.getElementById('usuariosPagination');

                const renderChips = (items, container, kind) => {
                    if (!container) return;
                    container.innerHTML = items.map(val => `
                        <button type="button" class="btn btn-sm ${kind}-chip ${kind}-chip-item btn-outline-primary" data-value="${String(val)}">
                            ${String(val)}
                        </button>
                    `).join('');
                    container.querySelectorAll(`.${kind}-chip-item`).forEach(btn => {
                        btn.addEventListener('click', () => {
                            const value = btn.getAttribute('data-value');
                            if (kind === 'empresa') filtroEmpresa = (filtroEmpresa === value ? null : value);
                            if (kind === 'setor') filtroSetor = (filtroSetor === value ? null : value);
                            if (kind === 'estado') filtroEstado = (filtroEstado === value ? null : value);
                            pagina = 1;
                            update();
                        });
                    });
                };

                const filtrar = () => {
                    const termo = (filtroTexto || '').toLowerCase();
                    return usuariosData.filter(u => {
                        const texto = [u['Colaborador'], u['Email'], u['Empresa'], u['Setor'], u['Estado'], u['Centro de Custo']]
                            .map(x => (x || '').toString().toLowerCase()).join(' ');
                        if (termo && !texto.includes(termo)) return false;
                        if (filtroEmpresa && u['Empresa'] !== filtroEmpresa) return false;
                        if (filtroSetor && u['Setor'] !== filtroSetor) return false;
                        if (filtroEstado && u['Estado'] !== filtroEstado) return false;
                        return true;
                    });
                };

                const renderList = (arr) => {
                    listEl.innerHTML = arr.map(usuario => {
                        const fmtNumber = (n)=> Number(n||0).toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});
                        const valorUnitario = usuario['Valor Unitário'] ?? usuario['Valor UnitÃ¡rio'] ?? usuario['ValorUnitario'] ?? 0;
                        const totalNum = usuario['Total'] ?? usuario['total'] ?? 0;
                        const valorTotalStr = usuario['Valor Total'] || usuario['ValorTotal'] || (`R$ ${fmtNumber(totalNum)}`);
                        return `
                        <div class="user-card">
                            <div class="row">
                                <div class="col-md-8">
                                    <h6 class="mb-1"><strong>${usuario['Colaborador'] || ''}</strong></h6>
                                    <p class="mb-1 text-muted small">
                                        📧 ${usuario['Email'] || 'Sem email'}<br>
                                        🏢 ${usuario['Empresa'] || ''}<br>
                                        🏭 Setor: ${usuario['Setor'] || ''}<br>
                                        🗺️ Estado: ${usuario['Estado'] || ''}<br>
                                        🏦 Centro de Custo: ${usuario['Centro de Custo'] || ''}
                                    </p>
                                </div>
                                <div class="col-md-4 text-end">
                                    <p class="mb-1"><strong>Criação:</strong> ${usuario['Data de Criação'] || ''}</p>
                                    <p class="mb-1"><strong>Qtd:</strong> ${usuario['Quantidade'] ?? ''}</p>
                                    <p class="mb-1"><strong>Valor Unit:</strong> ${usuario['Valor Unitário']? 'R$ ' + Number(valorUnitario).toLocaleString('pt-BR', {minimumFractionDigits:2}): ''}</p>
                                    <p class="mb-0"><strong>Valor Total:</strong> ${valorTotalStr}</p>
                                </div>
                            </div>
                        </div>`;
                    }).join('');
                };

                const renderPager = (total, page, perPage) => {
                    const totalPages = Math.max(1, Math.ceil(total / perPage));
                    const prevDisabled = page <= 1 ? 'disabled' : '';
                    const nextDisabled = page >= totalPages ? 'disabled' : '';
                    pagerEl.innerHTML = `
                        <div class="small text-muted">Exibindo página ${page} de ${totalPages} (total ${total} usuários)</div>
                        <div>
                            <button class="btn btn-sm btn-outline-secondary me-2" id="usuarios-prev" ${prevDisabled}>Anterior</button>
                            <button class="btn btn-sm btn-outline-secondary" id="usuarios-next" ${nextDisabled}>Próxima</button>
                        </div>
                    `;
                    const prev = document.getElementById('usuarios-prev');
                    const next = document.getElementById('usuarios-next');
                    if (prev) prev.onclick = () => { if (pagina > 1) { pagina--; update(); } };
                    if (next) next.onclick = () => { pagina++; update(); };
                };

                const update = () => {
                    filtroTexto = (input.value || '');
                    const filtrados = filtrar();
                    const total = filtrados.length;
                    const totalPages = Math.max(1, Math.ceil(total / porPagina));
                    if (pagina > totalPages) pagina = totalPages;
                    const inicio = (pagina - 1) * porPagina;
                    const pageArr = filtrados.slice(inicio, inicio + porPagina);
                    renderList(pageArr);
                    renderPager(total, pagina, porPagina);

                    // Marcar chips ativos
                    const toggleActive = (container, kind, current) => {
                        if (!container) return;
                                container.querySelectorAll(`.${kind}-chip-item`).forEach(btn => {
                                    const value = btn.getAttribute('data-value');
                                    btn.classList.toggle('btn-primary', current === value);
                                    btn.classList.toggle('btn-outline-primary', current !== value);
                                });
                            };
                            toggleActive(chipsEmpresa, 'empresa', filtroEmpresa);
                            toggleActive(chipsSetor, 'setor', filtroSetor);
                            toggleActive(chipsEstado, 'estado', filtroEstado);
                        };

                        input.addEventListener('input', () => { pagina = 1; update(); });
                        clearBtn.addEventListener('click', () => { input.value = ''; pagina = 1; update(); input.focus(); });
                        if (chipsClear) chipsClear.addEventListener('click', () => {
                            filtroEmpresa = null; filtroSetor = null; filtroEstado = null; pagina = 1; update();
                        });

                        renderChips(empresas, chipsEmpresa, 'empresa');
                        renderChips(setores, chipsSetor, 'setor');
                        renderChips(estados, chipsEstado, 'estado');
                        console.log('Chips renderizados');
                        
                update();
                console.log('=== FIM mostrarUsuarios (SUCESSO) ===');
            })
            .catch(error => {
                console.error('=== ERRO AO CARREGAR USUÁRIOS ===');
                console.error('Tipo do erro:', error.constructor.name);
                console.error('Mensagem:', error.message);
                console.error('Stack:', error.stack);
                modalBody.innerHTML = `
                    <div class="alert alert-danger">
                        <strong>Erro ao carregar usuários:</strong><br>
                        ${error.message || 'Por favor, tente novamente.'}
                    </div>
                `;
            });
    }
    </script>
    <script>
    // Fallback/global handler para abrir a modal de TODOS os usuários ao clicar no KPI
    (function(){
        function buildAndRenderTable(usuarios, container, page=1, pageSize=25){
            if(!Array.isArray(usuarios)) usuarios = [];
            const keys = Object.keys(usuarios[0] || {});
            // Ensure 'Valor Total' column exists (prefer server formatted string)
            if(!keys.includes('Valor Total')) keys.push('Valor Total');
            const start = (page-1)*pageSize;
            const pageItems = usuarios.slice(start, start+pageSize);

            let html = '<div class="table-responsive"><table class="table table-sm table-striped"><thead><tr>';
            for(const k of keys) html += `<th>${k}</th>`;
            html += '</tr></thead><tbody>';
            for(const row of pageItems){
                html += '<tr>';
                for(const k of keys){ 
                    let val = row[k]===null||row[k]===undefined? '': row[k];
                    // prefer formatted server string for Valor Total
                    if(k === 'Valor Total'){
                        val = row['Valor Total'] || row['ValorTotal'] || (row['Total'] ? ('R$ ' + Number(row['Total']).toLocaleString('pt-BR', {minimumFractionDigits:2})) : 'R$ 0,00');
                    }
                    html += `<td>${val}</td>`;
                }
                html += '</tr>';
            }
            html += `</tbody></table></div>`;

            const totalPages = Math.max(1, Math.ceil(usuarios.length / pageSize));
            html += '<nav><ul class="pagination pagination-sm">';
            for(let p=1;p<=totalPages;p++){
                html += `<li class="page-item ${p===page?'active':''}"><a href="#" class="page-link" data-page="${p}">${p}</a></li>`;
            }
            html += '</ul></nav>';

            container.innerHTML = html;
            container.querySelectorAll('.page-link').forEach(a=>{
                a.addEventListener('click', function(e){
                    e.preventDefault();
                    const p = parseInt(this.getAttribute('data-page'))||1;
                    buildAndRenderTable(usuarios, container, p, pageSize);
                })
            })
        }

        function openAllUsersModal(){
            const modalEl = document.getElementById('modalUsuarios');
            const modalBody = document.getElementById('modalBody');
            const modalTitle = document.getElementById('modalTitle');
            if(!modalEl || !modalBody || !modalTitle) return;
            modalTitle.textContent = '👥 Todos os Usuários';
            modalBody.innerHTML = '<p>Carregando usuários...</p>';
            const bs = new bootstrap.Modal(modalEl);
            bs.show();

            fetch('/api/usuarios').then(r=>{
                if(!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            }).then(data=>{
                const usuarios = (data && data.usuarios) ? data.usuarios : [];
                if(usuarios.length === 0){
                    modalBody.innerHTML = '<div class="alert alert-info">Nenhum usuário encontrado.</div>';
                    return;
                }
                buildAndRenderTable(usuarios, modalBody, 1, 25);
            }).catch(err=>{
                console.error('Falha ao carregar todos os usuários (global):', err);
                modalBody.innerHTML = `<div class="alert alert-danger">Erro ao carregar usuários: ${err.message}</div>`;
            });
        }

        document.addEventListener('DOMContentLoaded', function(){
            const kpi = document.getElementById('kpi-total-usuarios');
            if(kpi){
                kpi.style.cursor = 'pointer';
                kpi.addEventListener('click', function(e){
                    try{ openAllUsersModal(); }catch(ex){ console.error(ex); }
                });
            }
        });
    })();
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
                               'qtdLicenca', 'valorUnitarioMensal', 'valorTotalLicenca', 'DataCriacaoFormatada']]
    
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
        'valorTotalLicenca': 'Total',
        'DataCriacaoFormatada': 'Data de Criação'
    })

    # Formatar a data para dd/mm/aaaa para JSON
    if 'Data de Criação' in usuarios.columns:
        try:
            usuarios['Data de Criação'] = usuarios['Data de Criação'].apply(
                lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else (str(x) if pd.notna(x) else None)
            )
        except Exception as _:
            usuarios['Data de Criação'] = usuarios['Data de Criação'].astype(str)

    # Garantir que Total não tenha NaN: usar fallback Valor Unitário * Quantidade quando Total faltar
    try:
        if 'Total' in usuarios.columns:
            usuarios['Valor Unitário'] = pd.to_numeric(usuarios['Valor Unitário'], errors='coerce').fillna(0)
            usuarios['Quantidade'] = pd.to_numeric(usuarios['Quantidade'], errors='coerce').fillna(0)
            usuarios['Total'] = pd.to_numeric(usuarios['Total'], errors='coerce')
            # Calcular Total quando estiver NaN
            mask_nan = pd.isna(usuarios['Total'])
            usuarios.loc[mask_nan, 'Total'] = usuarios.loc[mask_nan, 'Valor Unitário'] * usuarios.loc[mask_nan, 'Quantidade']
            # Garantir que Total seja 0 se ainda for NaN
            usuarios['Total'] = usuarios['Total'].fillna(0)
    except Exception as e:
        app.logger.error(f"Erro ao processar Total: {e}")

    # Substituir TODOS os NaN por 0 em colunas numéricas
    numeric_cols = ['Valor Unitário', 'Quantidade', 'Total']
    for col in numeric_cols:
        if col in usuarios.columns:
            usuarios[col] = usuarios[col].fillna(0)
    
    # Substituir NaN por None em outras colunas
    usuarios = usuarios.replace({pd.NA: None, np.nan: None})
    
    # Converter para dicionário
    usuarios_dict = usuarios.to_dict(orient='records')

    # Adicionar coluna formatada para exibição: Valor Total (string em R$)
    try:
        usuarios['Valor Total'] = usuarios['Total'].apply(lambda v: f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if v is not None else None)
    except Exception:
        # se algo falhar, garantir coluna presente
        usuarios['Valor Total'] = usuarios['Total'].apply(lambda v: str(v) if v is not None else None)

    # Re-converter dicionário para incluir a nova coluna ordenada no final
    usuarios_dict = usuarios.to_dict(orient='records')
    
    # Limpar qualquer NaN que ainda possa existir (fallback final)
    usuarios_list = []
    for user in usuarios_dict:
        cleaned_user = {}
        for k, v in user.items():
            # Usar pd.isna() que é mais robusto
            if pd.isna(v):
                cleaned_user[k] = 0 if k in numeric_cols else None
            else:
                cleaned_user[k] = v
        usuarios_list.append(cleaned_user)
    
    # DEBUG: Verificar quantos NaNs ainda existem
    nan_count = sum(1 for user in usuarios_list for v in user.values() if pd.isna(v))
    app.logger.info(f"DEBUG: {nan_count} valores NaN encontrados após limpeza")
    
    # Log para debug
    app.logger.info(f"Retornando {len(usuarios_list)} usuários para licença '{licenca}'")
    
    # Contar total de usuários
    total_usuarios = len(usuarios_list)

    # Retornar usando Response com JSON manual para evitar NaN
    response_data = {'total_usuarios': total_usuarios, 'usuarios': usuarios_list}
    return Response(
        json.dumps(response_data, ensure_ascii=False, allow_nan=False),
        mimetype='application/json'
    )


@app.route('/api/usuarios', methods=['GET'])
def api_usuarios_all():
    """Retorna todos os usuários (sem filtro de licença)"""
    df = load_data()
    # Selecionar colunas relevantes (mesmas usadas no endpoint por licença)
    usuarios = df[['nomeColaborador', 'email', 'empresa', 'setor', 'estado', 'Centro de Custo',
                   'qtdLicenca', 'valorUnitarioMensal', 'valorTotalLicenca', 'DataCriacaoFormatada']].copy()

    usuarios = usuarios.rename(columns={
        'nomeColaborador': 'Colaborador',
        'email': 'Email',
        'empresa': 'Empresa',
        'setor': 'Setor',
        'estado': 'Estado',
        'Centro de Custo': 'Centro de Custo',
        'qtdLicenca': 'Quantidade',
        'valorUnitarioMensal': 'Valor Unitário',
        'valorTotalLicenca': 'Total',
        'DataCriacaoFormatada': 'Data de Criação'
    })

    # Normalizar e limpar
    try:
        usuarios['Valor Unitário'] = pd.to_numeric(usuarios['Valor Unitário'], errors='coerce').fillna(0)
        usuarios['Quantidade'] = pd.to_numeric(usuarios['Quantidade'], errors='coerce').fillna(0)
        usuarios['Total'] = pd.to_numeric(usuarios['Total'], errors='coerce')
        mask_nan = pd.isna(usuarios['Total'])
        usuarios.loc[mask_nan, 'Total'] = usuarios.loc[mask_nan, 'Valor Unitário'] * usuarios.loc[mask_nan, 'Quantidade']
        usuarios['Total'] = usuarios['Total'].fillna(0)
    except Exception as e:
        app.logger.error(f"Erro ao processar Totais (all): {e}")

    # Substituir NaN por None e preparar para JSON
    usuarios = usuarios.replace({pd.NA: None, np.nan: None})

    # Converter objetos datetime/timestamp para strings ISO para garantir serialização JSON
    if 'Data de Criação' in usuarios.columns:
        try:
            usuarios['Data de Criação'] = usuarios['Data de Criação'].apply(
                lambda x: x.isoformat() if hasattr(x, 'isoformat') else (str(x) if x is not None else None)
            )
        except Exception:
            # Fallback mais simples
            usuarios['Data de Criação'] = usuarios['Data de Criação'].astype(str).replace('NaT', None)

    usuarios_dict = usuarios.to_dict(orient='records')

    # Limpeza final
    usuarios_list = []
    for user in usuarios_dict:
        cleaned = {}
        for k, v in user.items():
            if v != v:
                cleaned[k] = 0 if k in ['Quantidade', 'Total', 'Valor Unitário'] else None
            else:
                cleaned[k] = v
        usuarios_list.append(cleaned)

    # Adicionar campo formatado 'Valor Total' (string) em cada usuário para exibição
    for u in usuarios_list:
        try:
            tot = u.get('Total')
            if tot is None:
                u['Valor Total'] = None
            else:
                u['Valor Total'] = f"R$ {float(tot):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except Exception:
            u['Valor Total'] = str(u.get('Total')) if u.get('Total') is not None else None

    response_data = {'total_usuarios': len(usuarios_list), 'usuarios': usuarios_list}
    return Response(json.dumps(response_data, ensure_ascii=False, allow_nan=False), mimetype='application/json')


@app.route('/api/rateio_contrato', methods=['GET'])
def api_rateio_contrato():
    """Gera o rateio por contrato (empresa + licença + modalidade) por Centro de Custo e exporta CSV."""
    empresa = request.args.get('empresa')
    licenca = request.args.get('licenca')
    modalidade = request.args.get('modalidade')
    if not empresa or not licenca:
        return jsonify({'error': 'Parâmetros obrigatórios ausentes: empresa e licenca'}), 400

    df = load_data()
    # Filtro por contrato (empresa + licenca [+ modalidade quando fornecida])
    mask = (
        (df['empresa'].astype(str) == str(empresa)) &
        (df['licenca'].astype(str) == str(licenca))
    )
    if modalidade:
        mask &= (df['modalidadeLicenca'].astype(str) == str(modalidade))

    dados = df[mask].copy()
    if dados.empty:
        return jsonify({'error': 'Nenhum dado encontrado para o contrato informado.'}), 404

    # Cálculos por Centro de Custo
    # - Quantidade por Centro de Custo: soma de qtdLicenca
    # - Valor por Centro de Custo: soma de valorTotalLicenca
    # - % por Centro de Custo: (valor_cc / valor_total_contrato) * 100
    dados['qtdLicenca'] = pd.to_numeric(dados['qtdLicenca'], errors='coerce')
    dados['valorTotalLicenca'] = pd.to_numeric(dados['valorTotalLicenca'], errors='coerce')
    grp = dados.groupby('Centro de Custo', dropna=False).agg({
        'qtdLicenca': 'sum',
        'valorTotalLicenca': 'sum'
    }).reset_index().rename(columns={
        'Centro de Custo': 'centro_custo',
        'qtdLicenca': 'qtd_cc',
        'valorTotalLicenca': 'valor_cc'
    })

    valor_total = grp['valor_cc'].sum()
    # Evitar divisão por zero
    grp['perc_cc'] = grp['valor_cc'].apply(lambda v: (float(v) / float(valor_total) * 100) if pd.notna(v) and valor_total not in [0, None] else 0.0)

    # Montar DataFrame final com colunas solicitadas
    out = grp.copy()
    out.insert(0, 'licenca', str(licenca))
    out.insert(0, 'empresa', str(empresa))
    # Renomear para os rótulos finais em PT-BR
    out = out.rename(columns={
        'qtd_cc': 'qtd (por centro de custo)',
        'valor_cc': 'valor por centro de custo',
        'perc_cc': '% por centro de custo'
    })

    # Ordenar por valor decrescente
    out = out.sort_values('valor por centro de custo', ascending=False)

    # Formatação: números com separador decimal "," e separador de milhar "." na exportação CSV
    def fmt_val(v):
        try:
            return (f"{float(v):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        except Exception:
            return ''

    out_fmt = out.copy()
    out_fmt['valor por centro de custo'] = out_fmt['valor por centro de custo'].apply(fmt_val)
    out_fmt['% por centro de custo'] = out_fmt['% por centro de custo'].apply(lambda x: f"{float(x):.2f}".replace('.', ',') if pd.notna(x) else '')

    # Gerar CSV com separador ;
    csv_lines = []
    columns = ['empresa', 'licenca', 'qtd (por centro de custo)', 'centro_custo', 'valor por centro de custo', '% por centro de custo']
    csv_lines.append(';'.join(columns))
    for _, row in out_fmt.iterrows():
        vals = [
            str(row.get('empresa', '')),
            str(row.get('licenca', '')),
            str(int(row.get('qtd (por centro de custo)', 0))) if pd.notna(row.get('qtd (por centro de custo)')) else '0',
            str(row.get('centro_custo', '')),
            str(row.get('valor por centro de custo', '')),
            str(row.get('% por centro de custo', ''))
        ]
        csv_lines.append(';'.join(vals))

    csv_data = '\n'.join(csv_lines)
    # Nome de arquivo amigável
    file_name = f"rateio_{re.sub(r'[^a-zA-Z0-9_-]+', '_', str(empresa))}_{re.sub(r'[^a-zA-Z0-9_-]+', '_', str(licenca))}"
    if modalidade:
        file_name += f"_{re.sub(r'[^a-zA-Z0-9_-]+', '_', str(modalidade))}"
    file_name += '.csv'

    headers = {
        'Content-Disposition': f'attachment; filename="{file_name}"',
        'Content-Type': 'text/csv; charset=utf-8'
    }
    return Response(csv_data, headers=headers)


@app.route('/api/rateio_contratos', methods=['POST'])
def api_rateio_contratos():
    """Gera rateio consolidado para múltiplos contratos selecionados e exporta CSV."""
    data = request.get_json(silent=True)
    if not data or 'contracts' not in data or not isinstance(data['contracts'], list) or len(data['contracts']) == 0:
        return jsonify({'error': 'Nenhum contrato informado'}), 400

    contratos = data['contracts']
    df = load_data()

    # Construir máscara que combine qualquer um dos contratos fornecidos
    masks = []
    for c in contratos:
        emp = str(c.get('empresa', '')).strip()
        lic = str(c.get('licenca', '')).strip()
        mod = str(c.get('modalidade', '')).strip()
        m = (df['empresa'].astype(str) == emp) & (df['licenca'].astype(str) == lic)
        if mod:
            m &= (df['modalidadeLicenca'].astype(str) == mod)
        masks.append(m)

    if len(masks) == 0:
        return jsonify({'error': 'Nenhum contrato válido fornecido.'}), 400

    # Combinar máscaras usando OR
    import functools, operator
    mask_total = functools.reduce(operator.or_, masks)
    dados = df[mask_total].copy()

    if dados.empty:
        return jsonify({'error': 'Nenhum dado encontrado para os contratos selecionados.'}), 404

    # Agrupar por Centro de Custo
    dados['qtdLicenca'] = pd.to_numeric(dados['qtdLicenca'], errors='coerce').fillna(0)
    dados['valorTotalLicenca'] = pd.to_numeric(dados['valorTotalLicenca'], errors='coerce').fillna(0)
    grp = dados.groupby('Centro de Custo', dropna=False).agg({
        'qtdLicenca': 'sum',
        'valorTotalLicenca': 'sum'
    }).reset_index().rename(columns={
        'Centro de Custo': 'centro_custo',
        'qtdLicenca': 'qtd_cc',
        'valorTotalLicenca': 'valor_cc'
    })

    valor_total = grp['valor_cc'].sum()
    grp['perc_cc'] = grp['valor_cc'].apply(lambda v: (float(v) / float(valor_total) * 100) if valor_total not in [0, None] else 0.0)

    # Montar saída
    out = grp.copy()
    empresas_sel = sorted(list(set([c.get('empresa','') for c in contratos])))
    licencas_sel = sorted(list(set([c.get('licenca','') for c in contratos])))
    empresas_label = '|'.join(empresas_sel)
    licencas_label = '|'.join(licencas_sel)
    out.insert(0, 'licenca', licencas_label)
    out.insert(0, 'empresa', empresas_label)

    out = out.rename(columns={
        'qtd_cc': 'qtd (por centro de custo)',
        'valor_cc': 'valor por centro de custo',
        'perc_cc': '% por centro de custo'
    })

    out = out.sort_values('valor por centro de custo', ascending=False)

    # Formatação
    def fmt_val(v):
        try:
            return (f"{float(v):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        except Exception:
            return ''

    out_fmt = out.copy()
    out_fmt['valor por centro de custo'] = out_fmt['valor por centro de custo'].apply(fmt_val)
    out_fmt['% por centro de custo'] = out_fmt['% por centro de custo'].apply(lambda x: f"{float(x):.2f}".replace('.', ',') if pd.notna(x) else '')

    columns = ['empresa', 'licenca', 'qtd (por centro de custo)', 'centro_custo', 'valor por centro de custo', '% por centro de custo']
    csv_lines = [';'.join(columns)]
    for _, row in out_fmt.iterrows():
        vals = [
            str(row.get('empresa', '')),
            str(row.get('licenca', '')),
            str(int(row.get('qtd (por centro de custo)', 0))) if pd.notna(row.get('qtd (por centro de custo)')) else '0',
            str(row.get('centro_custo', '')),
            str(row.get('valor por centro de custo', '')),
            str(row.get('% por centro de custo', ''))
        ]
        csv_lines.append(';'.join(vals))

    csv_data = '\n'.join(csv_lines)
    file_name = 'rateio_consolidado.csv'

    headers = {
        'Content-Disposition': f'attachment; filename="{file_name}"',
        'Content-Type': 'text/csv; charset=utf-8'
    }
    return Response(csv_data, headers=headers)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
