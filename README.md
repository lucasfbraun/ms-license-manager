<<<<<<< HEAD
# ms-license-manager
=======
# 📊 Dashboard de Licenciamento Microsoft

## 🐳 Início Rápido com Docker (RECOMENDADO)

```powershell
# 1. Construir e iniciar
docker-compose up -d --build

# 2. Acessar o dashboard
http://localhost:5000

# 3. Parar o dashboard
docker-compose down
```

**📖 Guia completo de Docker**: Veja [GUIA_DOCKER.md](GUIA_DOCKER.md) para troubleshooting e configurações avançadas

---

## 🎯 Visão Geral

Este projeto oferece **três versões** de dashboards interativos para análise e controle de licenças Microsoft:

1. **Dashboard Flask (Python)** - Versão profissional com servidor web e filtros
2. **Dashboard HTML com Filtros** - Versão standalone com filtros interativos
3. **Dashboard HTML Simples** - Versão básica sem filtros

---

## 📁 Arquivos do Projeto

```
📂 Licenciamento Microsoft/
├── 📊 LICENCIAMENTO MICROSOFT (1).xlsx  # Sua planilha de dados
├── 🐍 dashboard_flask.py                # Dashboard Python Flask (COM FILTROS)
├── 🌐 dashboard_filtros.html            # Dashboard HTML standalone (COM FILTROS)
├── 🌐 dashboard.html                    # Dashboard HTML simples
├── 🔍 analyze_data.py                   # Script de análise de dados
├── 🐳 Dockerfile                        # Configuração Docker
├── 🐳 docker-compose.yml                # Orquestração Docker
├── 📦 requirements.txt                  # Dependências Python
└── 📖 README.md                         # Este arquivo
```

---

## 🚀 Opção 1: Dashboard Flask (Recomendado - COM FILTROS)

### ✨ Vantagens
- ✅ Filtros interativos por: Empresa, Estado, Setor, Centro de Custo, Licença, Modalidade
- ✅ Gráficos mais interativos e profissionais
- ✅ Melhor performance com grandes volumes de dados
- ✅ Atualização instantânea ao aplicar filtros

### 📦 Dependências (já instaladas)
- pandas
- openpyxl
- plotly
- flask

### ▶️ Como Usar

1. **Abra o terminal no VS Code** (Ctrl + ')

2. **Execute o dashboard:**
   ```powershell
   python dashboard_flask.py
   ```

3. **Acesse no navegador:**
   ```
   http://127.0.0.1:5000
   ```
   ou
   ```
   http://localhost:5000
   ```

4. **Usando os Filtros:**
   - Selecione os filtros desejados (Empresa, Estado, Setor, etc.)
   - Clique em "🔍 Aplicar Filtros"
   - Os gráficos e KPIs serão atualizados instantaneamente
   - Use "🔄 Limpar Filtros" para ver todos os dados novamente

5. **Atualizando dados da planilha:**
   - Edite a planilha Excel e salve
   - Pressione F5 no navegador para recarregar

6. **Para parar o servidor:**
   - Pressione `Ctrl + C` no terminal

---

## 🌐 Opção 2: Dashboard HTML com Filtros (Mais Fácil!)

### ✨ Vantagens
- ✅ **Filtros interativos** por 6 categorias diferentes
- ✅ Não precisa de servidor rodando
- ✅ Funciona offline
- ✅ Arraste e solte a planilha
- ✅ Atualização instantânea ao aplicar filtros

### ▶️ Como Usar

1. **Abra o arquivo:**
   - Vá até: `C:\Users\Lucas Braun\Documents\Licenciamento Microsoft`
   - Clique duas vezes em `dashboard_filtros.html`

2. **Carregue a planilha:**
   - Arraste e solte a planilha `LICENCIAMENTO MICROSOFT (1).xlsx`
   - OU clique na área indicada para selecionar

3. **Use os Filtros:**
   - 📊 **Empresa** - Filtre por empresa específica
   - 🗺️ **Estado** - Analise por região
   - 🏢 **Setor** - Veja gastos departamentais
   - 🏦 **Centro de Custo** - Foque em centros específicos
   - 📋 **Licença** - Filtre por tipo de licença
   - 💳 **Modalidade** - Cloud, On-Premise, etc.
   
4. **Aplicar Filtros:**
   - Selecione os filtros desejados
   - Clique em "🔍 Aplicar Filtros"
   - Gráficos atualizam instantaneamente!

5. **Atualizando dados:**
   - Edite a planilha Excel e salve
   - Recarregue a planilha no dashboard (arraste novamente)

---

## 📄 Opção 3: Dashboard HTML Simples (Sem Filtros)

## 📄 Opção 3: Dashboard HTML Simples (Sem Filtros)

Versão básica sem filtros, apenas visualização dos dados.

- Abra o arquivo `dashboard.html`
- Arraste a planilha Excel
- Veja os gráficos (sem opção de filtrar)

---

## 📊 Funcionalidades dos Dashboards

### 🔍 **FILTROS DISPONÍVEIS** (Opções 1 e 2)

Filtre seus dados por:

1. **🏢 Empresa** - Analise gastos por empresa específica
2. **🗺️ Estado** - Veja distribuição regional
3. **🏭 Setor** - Foque em departamentos específicos
4. **🏦 Centro de Custo** - Analise centros de custo individualmente
5. **📋 Licença** - Filtre por tipo de licença (Office 365, Microsoft 365, etc.)
6. **💳 Modalidade** - Cloud vs On-Premise

**Combine múltiplos filtros** para análises mais específicas!

Exemplo: Ver gastos de "EMPRESA X" + "Estado SP" + "Setor TI"

### 📈 KPIs Principais
- 💰 **Gasto Total** - Valor total investido em licenças
- 👥 **Total de Usuários** - Quantidade de usuários com licenças
- 🏢 **Empresas** - Número de empresas cadastradas
- 📋 **Licenças** - Total de licenças ativas

### 📉 Gráficos Disponíveis

1. **💼 Gastos por Empresa**
   - Top 15 empresas que mais gastam
   - Gráfico de barras horizontal

2. **🗺️ Distribuição por Estado**
   - Gastos totais por região
   - Gráfico de pizza/rosca

3. **🏦 Top 10 Centros de Custo**
   - Centros de custo com maiores gastos
   - Identifica onde o dinheiro está sendo gasto

4. **📊 Distribuição de Licenças**
   - Top 10 licenças mais utilizadas
   - Quantidade por tipo de licença

5. **💳 Gastos por Modalidade**
   - Cloud vs On-Premise
   - Distribuição de custos por tipo

6. **🏢 Gastos por Setor**
   - Top 15 setores com maiores gastos
   - Análise departamental

7. **🔄 Distribuição por Fornecedor**
   - Gastos por faturador (Ingram, etc.)
   - Visão de fornecedores

### 📋 Recursos Adicionais

- **⚠️ Alertas de Contratos** (Dashboard Python)
  - Mostra contratos vencendo nos próximos 90 dias
  - Ajuda no planejamento de renovações

- **📊 Tabela Detalhada**
  - Visualização dos primeiros 50 registros
  - Dados completos de empresa, usuário, licença, etc.

---

## 🔄 Workflow de Atualização

### Processo Recomendado:

1. **Edite a planilha Excel** normalmente
   - Adicione novos usuários
   - Atualize valores
   - Modifique licenças

2. **Salve o arquivo** (Ctrl + S)

3. **Dashboard atualiza automaticamente**
   - **Python**: Aguarde 1 minuto ou clique em "Atualizar"
   - **HTML**: Recarregue a planilha (arraste novamente)

---

## 💡 Insights Implementados

### Análises Disponíveis:

✅ **Controle de Gastos**
- Identifique empresas que mais gastam
- Monitore centros de custo críticos
- Compare modalidades de licenciamento

✅ **Distribuição Geográfica**
- Visualize gastos por estado
- Planeje expansões regionais

✅ **Otimização de Licenças**
- Veja licenças mais utilizadas
- Identifique oportunidades de consolidação

✅ **Gestão de Fornecedores**
- Compare fornecedores
- Analise distribuição de compras

✅ **Análise Setorial**
- Gastos por departamento
- Identifique áreas que mais consomem licenças

---

## 🛠️ Troubleshooting

### Problema: Dashboard Python não inicia

**Solução:**
```powershell
# Reinstale as dependências
pip install --upgrade pandas openpyxl plotly dash dash-bootstrap-components
```

### Problema: Dashboard HTML não carrega planilha

**Solução:**
- Verifique se o arquivo é .xlsx
- Teste em outro navegador (Chrome recomendado)
- Certifique-se de que JavaScript está habilitado

### Problema: Dados não atualizam

**Solução Python:**
- Verifique se a planilha está salva
- Clique em "Atualizar Dados"
- Reinicie o servidor (Ctrl+C e rode novamente)

**Solução HTML:**
- Recarregue a planilha manualmente
- Atualize a página (F5)

---

## 📚 Guias Disponíveis

- **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** - ⚡ Comece aqui! Guia de 3 passos
- **[GUIA_DOCKER.md](GUIA_DOCKER.md)** - 🐳 Tudo sobre Docker (troubleshooting, comandos, deploy)
- **[GUIA_FILTROS.md](GUIA_FILTROS.md)** - 🔍 Como usar os 6 tipos de filtros
- **[GUIA_CONTRATOS.md](GUIA_CONTRATOS.md)** - 📅 Sistema de alertas de contratos

---

## 🎨 Personalizações Futuras

### Ideias para expandir:

- 📧 **Alertas por Email** - Notificações de contratos vencendo
- 📱 **Versão Mobile** - Dashboard responsivo
- 📊 **Exportar Relatórios** - PDF/Excel dos gráficos
- 🔐 **Login/Autenticação** - Controle de acesso
- 📈 **Previsões** - Machine Learning para prever gastos
- 🔔 **Webhooks** - Integração com Teams/Slack

---

## 📞 Suporte

Dúvidas ou sugestões? 
- Edite os arquivos conforme necessário
- Customize cores e estilos no HTML/CSS
- Adicione novos gráficos baseados em suas necessidades

---

## 🎉 Próximos Passos

1. ✅ Teste ambos os dashboards
2. ✅ Escolha o que melhor atende suas necessidades
3. ✅ Personalize cores e títulos
4. ✅ Adicione novos insights conforme necessário
5. ✅ Compartilhe com sua equipe

**Bom controle de licenças! 🚀**
>>>>>>> ac181b0 (versão inicial do projeto, rodando em docker)
