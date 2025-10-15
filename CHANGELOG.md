# 📝 CHANGELOG - Dashboard de Licenciamento Microsoft

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

---

## [1.0.0] - Docker Production Release

### 🐳 Adicionado - Containerização
- **Dockerfile** completo com Python 3.11-slim
- **docker-compose.yml** com volume mount para Excel
- **requirements.txt** com versões fixadas das dependências
- **.dockerignore** para otimizar build
- **.env.example** para configurações personalizáveis

### 🚀 Adicionado - Scripts de Automação
- **iniciar_dashboard.bat** - Script Windows com menu interativo
- **iniciar_dashboard.ps1** - Script PowerShell com cores e parâmetros
- Detecção automática de pré-requisitos (Docker, Docker Compose)
- Abertura automática do navegador após iniciar

### 📖 Adicionado - Documentação
- **GUIA_DOCKER.md** - Guia completo de Docker (35+ comandos e soluções)
- **INICIO_RAPIDO.md** - Guia de 3 passos para início rápido
- **RESUMO_DOCKER.md** - Visão geral da containerização

### 🔧 Modificado
- **dashboard_flask.py** - Detecta ambiente Docker automaticamente
- **dashboard_flask.py** - Bind em 0.0.0.0 quando em container
- **README.md** - Adicionada seção Docker no topo
- **README.md** - Links para novos guias e documentação

### ✨ Recursos
- Volume mount permite atualizar Excel sem rebuild do container
- Auto-restart em caso de falha
- Logs centralizados via docker-compose
- Scripts com verificação de status e troubleshooting

---

## [0.9.0] - Controle de Contratos

### 📅 Adicionado
- **Sistema de alertas de contratos** com 4 níveis de cores:
  - 🔴 Vermelho: Vencido ou vence hoje
  - 🟡 Amarelo: Vence em ≤7 dias
  - 🔵 Azul: Vence em ≤30 dias
  - ⚪ Branco: Mais de 30 dias
- **Tabela de contratos** no final do dashboard
- Cálculo automático de dias restantes
- **GUIA_CONTRATOS.md** - Documentação do sistema

### 🔧 Modificado
- **dashboard_flask.py** - Função `gerar_tabela_contratos()`
- **dashboard_flask.py** - CSS para cores de alerta
- Template HTML com seção de contratos

---

## [0.8.0] - Visualização de Usuários

### 👥 Adicionado
- **Modal de usuários** - Clique em licença para ver todos os usuários
- **API endpoint** `/api/usuarios/<licenca>` retorna JSON com dados
- Detalhes mostrados: Nome, Email, Empresa, Setor, Estado, Centro Custo, Quantidade, Valores
- Badges clicáveis nas licenças mais usadas
- JavaScript para requisição AJAX e exibição do modal

### 🔧 Modificado
- **dashboard_flask.py** - Nova rota API
- **dashboard_flask.py** - Função `get_usuarios_licenca()`
- Template HTML com modal Bootstrap

---

## [0.7.0] - Sistema de Filtros

### 🔍 Adicionado
- **6 tipos de filtros** interativos:
  1. Empresa
  2. Estado
  3. Setor
  4. Centro de Custo
  5. Licença
  6. Modalidade da Licença
- Barra lateral com filtros
- Botões "Aplicar Filtros" e "Limpar Filtros"
- **GUIA_FILTROS.md** - Documentação completa dos filtros

### 🔧 Modificado
- **dashboard_flask.py** - Função `apply_filters()`
- **dashboard_flask.py** - Rota `/` aceita query parameters
- Template HTML com sidebar de filtros
- Todos os gráficos atualizam com filtros aplicados

---

## [0.6.0] - Dashboard Flask Completo

### 📊 Adicionado
- **7 gráficos interativos** com Plotly:
  1. Gasto por Empresa (Pizza)
  2. Gasto por Licença (Barras horizontais)
  3. Timeline de Contratos (Linha do tempo)
  4. Gasto por Estado (Barras)
  5. Distribuição de Modalidades (Pizza)
  6. Licenças Mais Usadas (Barras)
  7. Gasto por Setor (Barras)
- **4 KPIs principais**:
  - Gasto Total
  - Total de Usuários
  - Número de Empresas
  - Número de Licenças
- Botão "Atualizar" para recarregar dados
- **dashboard_flask.py** - Aplicação Flask completa

### 🎨 Interface
- Design profissional com Bootstrap 5.3.0
- Cores personalizadas (tons de azul)
- Gráficos responsivos
- Ícones Font Awesome
- Efeitos hover e transições

---

## [0.5.0] - Dashboard HTML com Filtros

### 🌐 Adicionado
- **dashboard_filtros.html** - Versão standalone com filtros
- Leitura de Excel via SheetJS (drag-and-drop)
- Filtros client-side (sem servidor)
- 7 gráficos com Chart.js
- Processamento de dados em JavaScript

---

## [0.4.0] - Dashboard HTML Simples

### 🌐 Adicionado
- **dashboard.html** - Primeira versão do dashboard
- Gráficos básicos com Chart.js
- Leitura de Excel no navegador
- Sem necessidade de servidor
- Interface simples e funcional

---

## [0.3.0] - Migração Dash → Flask

### 🔄 Modificado
- **Migrado de Dash para Flask** devido a problemas de dependências
- Removido Dash e dependências problemáticas
- Implementado Flask + Plotly (mais estável)
- Corrigido erro de importação zmq/jupyter_client

### 🐛 Corrigido
- Conflito de dependências (ipykernel, jupyter_client, zmq)
- Corrupção de arquivo durante string replacement
- Erros de importação em ambiente Windows

---

## [0.2.0] - Análise de Dados

### 📈 Adicionado
- **analyze_data.py** - Script de análise exploratória
- Identificação de estrutura da planilha:
  - 196 linhas de dados
  - 15 colunas
  - Tipos de dados
  - Valores únicos por coluna
- Estatísticas descritivas
- Detecção de valores nulos

### 📊 Dados Identificados
- Empresas: 5 únicas
- Licenças: 36 tipos diferentes
- Estados: Múltiplos
- Modalidades: CSP, EA, etc.
- Datas: início e final de contrato
- Valores: unitário e total

---

## [0.1.0] - Versão Inicial

### 🎬 Adicionado
- Estrutura inicial do projeto
- Arquivo Excel "LICENCIAMENTO MICROSOFT (1).xlsx"
- README.md básico
- Identificação de requisitos
- Planejamento de features

---

## 🔮 Roadmap Futuro

### [1.1.0] - Segurança (Planejado)
- [ ] Sistema de autenticação (login/senha)
- [ ] Níveis de acesso (admin, viewer)
- [ ] JWT tokens para API
- [ ] HTTPS/SSL configurado

### [1.2.0] - Notificações (Planejado)
- [ ] Alertas por email de contratos vencendo
- [ ] Integração com Teams/Slack
- [ ] Webhooks personalizáveis
- [ ] Agendamento de relatórios

### [1.3.0] - Relatórios (Planejado)
- [ ] Exportar gráficos para PDF
- [ ] Exportar dados filtrados para Excel
- [ ] Templates de relatórios customizáveis
- [ ] Agendamento de exportações

### [1.4.0] - Analytics Avançado (Planejado)
- [ ] Previsões com Machine Learning
- [ ] Análise de tendências
- [ ] Sugestões de otimização de custos
- [ ] Comparações ano a ano

### [1.5.0] - Mobile (Planejado)
- [ ] Dashboard responsivo para mobile
- [ ] App móvel (PWA)
- [ ] Notificações push
- [ ] Modo offline

### [2.0.0] - Multi-tenant (Planejado)
- [ ] Suporte a múltiplas empresas
- [ ] Bancos de dados separados
- [ ] APIs públicas
- [ ] Marketplace de integrações

---

## 📊 Estatísticas do Projeto

### Linhas de Código
- Python: ~800 linhas (dashboard_flask.py)
- HTML/CSS/JS: ~600 linhas (templates)
- Documentação: ~2500 linhas (todos os .md)
- Scripts: ~400 linhas (.bat + .ps1)
- **Total: ~4300 linhas**

### Arquivos
- Código: 4 arquivos (.py, .html)
- Docker: 5 arquivos
- Scripts: 2 arquivos
- Documentação: 7 arquivos
- **Total: 18 arquivos**

### Recursos Implementados
- ✅ 7 gráficos interativos
- ✅ 6 tipos de filtros
- ✅ 4 KPIs
- ✅ 1 modal de detalhes
- ✅ 1 sistema de alertas
- ✅ 1 API endpoint
- ✅ Containerização Docker
- ✅ Scripts de automação

---

## 🏆 Marcos Importantes

- **2024-XX-XX**: Início do projeto
- **2024-XX-XX**: Primeira análise de dados
- **2024-XX-XX**: Dashboard HTML funcional
- **2024-XX-XX**: Dashboard Flask completo
- **2024-XX-XX**: Sistema de filtros implementado
- **2024-XX-XX**: Visualização de usuários adicionada
- **2024-XX-XX**: Controle de contratos implementado
- **2024-XX-XX**: Containerização Docker completa ✨

---

## 📝 Convenções de Versioning

Seguimos [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.x.x): Mudanças incompatíveis
- **MINOR** (x.1.x): Novas funcionalidades compatíveis
- **PATCH** (x.x.1): Correções de bugs

**Tags**:
- 🐳 Docker
- 📊 Gráficos
- 🔍 Filtros
- 📅 Contratos
- 👥 Usuários
- 📖 Documentação
- 🐛 Correções
- 🔧 Modificações
- ✨ Recursos
- 🚀 Deploy

---

**Última atualização**: Data atual  
**Versão atual**: 1.0.0 (Docker Production Release)
